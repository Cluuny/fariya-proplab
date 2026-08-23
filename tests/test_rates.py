"""test_rates.py — historical carry matrix (Bloque 2a).

The carry MUST be time-varying (historical policy rates), not a 2026 snapshot.
The load-bearing guard: EURUSD carry must be POSITIVE somewhere in 2009-2015
(EUR rates > USD rates then) — if it's negative across the whole history, the
historical series are not being applied.
"""

from __future__ import annotations

import pandas as pd
import pytest

from src import config, rates

_HAS_RATES = config.DATA_RATES.exists()
pytestmark = pytest.mark.skipif(
    not _HAS_RATES, reason="data/rates/policy_rates.csv ausente (descargar de BIS)"
)


def _daily_index():
    return pd.bdate_range("2004-01-01", "2026-08-14")


def test_eurusd_carry_positive_in_2009_2015():
    cm = rates.carry_matrix(_daily_index(), ["EURUSD"])
    window = cm.loc["2009-01-01":"2015-12-31", "EURUSD"]
    assert (window > 0).any(), "EURUSD carry nunca positivo en 2009-2015 → series históricas no aplicadas"
    # And it should be NEGATIVE recently (USD > EUR in 2024-2026).
    assert cm.loc["2024-01-01":, "EURUSD"].mean() < 0


def test_carry_is_time_varying():
    cm = rates.carry_matrix(_daily_index(), ["USDJPY"])
    s = cm["USDJPY"]
    # USDJPY carry was near zero in 2010-2015 (both ~0) and large positive in 2023+.
    assert s.loc["2010-01-01":"2015-12-31"].mean() < s.loc["2023-01-01":].mean()
    assert s.std() > 0


def test_cross_carry_is_additive():
    idx = _daily_index()
    cm = rates.carry_matrix(idx, ["EURUSD", "USDJPY", "EURJPY"])
    # log(EURJPY)=log(EURUSD)+log(USDJPY) → carries add, at every date.
    diff = (cm["EURJPY"] - (cm["EURUSD"] + cm["USDJPY"])).abs()
    assert diff.max() < 1e-12


def test_convention_factor_applied():
    # The 365/261 trading-day factor must be baked into the carry.
    idx = _daily_index()
    cm = rates.carry_matrix(idx, ["EURUSD"])
    r = rates.daily_policy_rates(idx)
    raw = (r["EUR"] - r["USD"]) / 100.0 / 360.0 * config.TRADING_DAY_SWAP_FACTOR
    assert (cm["EURUSD"] - raw).abs().max() < 1e-15
