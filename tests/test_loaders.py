"""Section 2 — data-pipeline: immutability, determinism, one parquet per
instrument, and detection of each anomaly kind on synthetic data."""

import hashlib

import numpy as np
import pandas as pd
import pytest

from src import loaders


def _write_csv(path, dates, close, extra=None):
    data = {"date": dates, "close": close}
    if extra:
        data.update(extra)
    pd.DataFrame(data).to_csv(path, index=False)
    return path


def _hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def clean_series(tmp_path):
    dates = pd.bdate_range("2020-01-01", periods=200)
    rng = np.random.default_rng(42)
    close = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, len(dates))))
    raw = tmp_path / "raw"
    raw.mkdir()
    _write_csv(raw / "EURUSD.csv", dates.strftime("%Y-%m-%d"), close)
    return raw, tmp_path / "clean"


def test_raw_is_immutable(clean_series):
    raw, clean = clean_series
    src = raw / "EURUSD.csv"
    before = _hash(src)
    loaders.run(raw_dir=raw, clean_dir=clean)
    assert _hash(src) == before


def test_deterministic_regeneration(clean_series):
    raw, clean = clean_series
    loaders.process_file(raw / "EURUSD.csv", clean)
    h1 = _hash(clean / "EURUSD.parquet")
    loaders.process_file(raw / "EURUSD.csv", clean)
    h2 = _hash(clean / "EURUSD.parquet")
    assert h1 == h2


def test_one_parquet_per_instrument(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    dates = pd.bdate_range("2020-01-01", periods=50).strftime("%Y-%m-%d")
    for sym in ("EURUSD", "GBPUSD", "USDJPY"):
        _write_csv(raw / f"{sym}.csv", dates, np.linspace(100, 110, 50))
    reports = loaders.run(raw_dir=raw, clean_dir=tmp_path / "clean")
    parquets = list((tmp_path / "clean").glob("*.parquet"))
    assert len(parquets) == 3
    assert len(reports) == 3


def test_clean_sorts_and_dedupes():
    df = pd.DataFrame(
        {"close": [3.0, 1.0, 2.0, 2.5]},
        index=pd.DatetimeIndex(
            ["2020-01-03", "2020-01-01", "2020-01-02", "2020-01-02"], name="date"
        ),
    )
    out = loaders.clean(df)
    assert out.index.is_monotonic_increasing
    assert not out.index.duplicated().any()
    assert out.loc["2020-01-02", "close"] == 2.5  # keep=last


def test_detect_nonpositive_price():
    dates = pd.bdate_range("2020-01-01", periods=10)
    close = np.full(10, 100.0)
    close[5] = 0.0
    df = pd.DataFrame({"close": close}, index=pd.DatetimeIndex(dates, name="date"))
    report = loaders.validate("X", df)
    assert any(a.kind == "nonpositive_price" for a in report.anomalies)


def test_detect_anomalous_return():
    dates = pd.bdate_range("2020-01-01", periods=60)
    close = np.full(60, 100.0)
    close[30] = 150.0  # large jump -> return > 5σ
    df = pd.DataFrame({"close": close}, index=pd.DatetimeIndex(dates, name="date"))
    report = loaders.validate("X", df)
    assert any(a.kind == "anomalous_return" for a in report.anomalies)


def test_detect_duplicate_dates():
    df = pd.DataFrame(
        {"close": [100.0, 101.0]},
        index=pd.DatetimeIndex(["2020-01-01", "2020-01-01"], name="date"),
    )
    report = loaders.validate("X", df, raw_had_duplicates=True)
    assert any(a.kind == "duplicate_dates" for a in report.anomalies)


def test_detect_calendar_gap():
    dates = list(pd.bdate_range("2020-01-01", periods=5)) + list(
        pd.bdate_range("2020-02-01", periods=5)
    )
    df = pd.DataFrame(
        {"close": np.full(10, 100.0)}, index=pd.DatetimeIndex(dates, name="date")
    )
    report = loaders.validate("X", df)
    assert report.missing_days > 0
    assert any(a.kind == "calendar_gap" for a in report.anomalies)


def _kinds(report):
    return {a.kind for a in report.anomalies}


def test_contract_jump_is_open_gap_not_anomalous_return():
    # Cierres suaves (sin retorno close-to-close anómalo) pero un GAP de apertura
    # grande en un día → contract_jump, NO anomalous_return.
    dates = pd.bdate_range("2020-01-01", periods=60)
    rng = np.random.default_rng(0)
    close = 100 + np.cumsum(rng.normal(0, 0.05, 60))   # muy suave
    open_ = close.copy()
    open_[30] = close[29] * 1.30                        # gap de apertura +30%
    df = pd.DataFrame({"open": open_, "close": close},
                      index=pd.DatetimeIndex(dates, name="date"))
    kinds = _kinds(loaders.validate("X", df))
    assert "contract_jump" in kinds
    assert "anomalous_return" not in kinds


def test_anomalous_return_without_open_gap():
    # Outlier close-to-close pero SIN gap de apertura (open_t = close_{t-1}) →
    # anomalous_return, NO contract_jump. Ya no coinciden.
    dates = pd.bdate_range("2020-01-01", periods=60)
    close = np.full(60, 100.0)
    close[30] = 150.0                                   # salto close-to-close
    open_ = np.empty(60)
    open_[0] = close[0]
    open_[1:] = close[:-1]                              # apertura = cierre previo
    df = pd.DataFrame({"open": open_, "close": close},
                      index=pd.DatetimeIndex(dates, name="date"))
    kinds = _kinds(loaders.validate("X", df))
    assert "anomalous_return" in kinds
    assert "contract_jump" not in kinds


def test_report_renders_all_instruments(clean_series):
    raw, clean = clean_series
    reports = loaders.run(raw_dir=raw, clean_dir=clean)
    md = loaders.render_report(reports)
    assert "EURUSD" in md
    assert "Reporte de calidad" in md
