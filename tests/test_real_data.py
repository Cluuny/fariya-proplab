"""Verificación EN CÓDIGO de los datos reales de Dukascopy.

Se SALTA si `data/clean/` no tiene parquets (los datos están gitignorados; en un
clon fresco no existen — corre `data/README.md` para poblarlos). Cuando existen,
confirma lo que el reporte de avance afirma: que corrimos loaders, qué obtuvimos,
y que el motor reproduce el Sharpe de referencia sobre datos reales (hito 2).
"""

import numpy as np
import pandas as pd
import pytest

from src import config, engine, loaders, signals

_PARQUETS = sorted(config.DATA_CLEAN.glob("*.parquet"))
pytestmark = pytest.mark.skipif(
    not _PARQUETS,
    reason="Sin data/clean/*.parquet — poblar data/raw/ (ver data/README.md) y correr python -m src.loaders",
)


def test_all_universe_instruments_present():
    have = {p.stem for p in _PARQUETS}
    missing = [i for i in config.INSTRUMENTS if i not in have]
    assert not missing, f"Faltan parquets: {missing}"


def test_prices_are_positive_and_dated():
    df = pd.read_parquet(config.DATA_CLEAN / "EURUSD.parquet")
    assert (df["close"] > 0).all()
    assert df.index.is_monotonic_increasing
    assert df.index.min().year <= 2004  # FX desde ~2003


def test_engine_reproduces_reference_sharpe_on_real_data():
    # Hito 2: buy&hold del índice de referencia reproduce SHARPE_REFERENCE.
    ref = config.SHARPE_REFERENCE
    prices = pd.DataFrame(
        {ref.instrument: pd.read_parquet(config.DATA_CLEAN / f"{ref.instrument}.parquet")["close"]}
    )
    # Gross (index) buy&hold — the index Sharpe excludes trading costs like swap.
    gross = engine.backtest(prices, signals.buy_and_hold(prices), apply_costs=False)
    got = engine.sharpe(gross)   # annualized with the series' own bars/year
    assert abs(got - ref.value) <= ref.tolerance, (
        f"Sharpe real {got:.3f} vs referencia externa {ref.value} (±{ref.tolerance})"
    )


def test_quality_report_flags_a_real_market_event():
    # Sobre una FX major, el validador marca al menos un retorno anómalo real.
    df = pd.read_parquet(config.DATA_CLEAN / "GBPUSD.parquet")
    report = loaders.validate("GBPUSD", df)
    kinds = [a.kind for a in report.anomalies]
    assert "anomalous_return" in kinds


def test_session_gap_no_longer_equals_anomalous_return():
    # El fix: los conteos ya NO coinciden (dejó de haber doble conteo).
    equal = 0
    for p in _PARQUETS:
        rep = loaders.validate(p.stem, pd.read_parquet(p))
        counts = rep.counts_by_kind()
        if counts.get("anomalous_return", 0) == counts.get("session_gap", -1):
            equal += 1
    # No pueden coincidir todos (antes coincidían los 10 por construcción).
    assert equal < len(_PARQUETS)
