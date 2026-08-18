"""test_tsmom.py — the TSMOM signal (H001) against the frozen contract.

Verifies direction, monthly rebalance with holding, the bounded-exposure
invariant, purity/determinism, and — the load-bearing one — that the vol-target
scaling is EX-ANTE (extending the series with future dates does not change past
weights; a look-ahead the engine's shift-guard cannot catch).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src import config, signals


def _synthetic(days: int = 900, seed: int = 0) -> pd.DataFrame:
    """Two instruments: UP trends up, DOWN trends down, over ~3 years."""
    idx = pd.bdate_range("2018-01-01", periods=days)
    t = np.arange(days)
    up = 100 * (1 + 0.0008) ** t          # steady uptrend
    down = 100 * (1 - 0.0006) ** t        # steady downtrend
    return pd.DataFrame({"UP": up, "DOWN": down}, index=idx)


def test_shape_and_columns():
    prices = _synthetic()
    w = signals.tsmom(prices)
    assert list(w.columns) == list(prices.columns)
    assert w.index.equals(prices.index)


def test_purity_and_determinism():
    prices = _synthetic()
    snapshot = prices.copy()
    w1 = signals.tsmom(prices)
    w2 = signals.tsmom(prices)
    assert prices.equals(snapshot), "tsmom must not mutate its input"
    assert w1.equals(w2), "tsmom must be deterministic"


def test_direction_follows_12m_sign():
    """ret_12m > 0 -> long (w > 0); ret_12m < 0 -> short (w < 0)."""
    prices = _synthetic()
    w = signals.tsmom(prices)
    # After a full year of lookback, on a live date the signs must be fixed.
    live = w[w.abs().sum(axis=1) > 0]
    last = live.iloc[-1]
    assert last["UP"] > 0, "an uptrending instrument must be long"
    assert last["DOWN"] < 0, "a downtrending instrument must be short"


def test_monthly_rebalance_holds_between():
    """Weights change only on rebalance dates; constant in between."""
    prices = _synthetic()
    w = signals.tsmom(prices)
    changes = (w.diff().abs().sum(axis=1) > 1e-12).sum()
    years = (w.index[-1] - w.index[0]).days / 365.25
    per_year = changes / years
    # ~12 rebalances/year (allow slack for the flat lookback head).
    assert 6 <= per_year <= 15, f"expected ~monthly, got {per_year:.1f}/yr"


def test_exposure_invariant():
    prices = _synthetic()
    w = signals.tsmom(prices)
    gross = w.abs().sum(axis=1)
    assert gross.max() <= config.MAX_GROSS_EXPOSURE + 1e-9
    # Conforms to the contract validator.
    signals.validate_weights(w)


def test_scaling_is_ex_ante():
    """Extending the series with FUTURE dates must not change past weights.

    The ex-ante property: the vol-target scalar at date t uses only volatility
    observed up to t (rolling std, shifted one day). If it used whole-series
    realized vol, appending future data would rewrite past weights — a
    signal-layer look-ahead the engine's shift-guard cannot see.
    """
    full = _synthetic(days=900)
    truncated = full.iloc[:600]
    w_trunc = signals.tsmom(truncated)
    w_full = signals.tsmom(full).loc[w_trunc.index]
    # Compare on the overlapping past dates.
    pd.testing.assert_frame_equal(w_trunc, w_full, atol=1e-12, rtol=0)
