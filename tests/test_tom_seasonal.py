"""test_tom_seasonal.py — the turn-of-the-month signal (H003) against the contract.

Verifies long-only, active only in the TOM window (~19% of days), the bounded-
exposure invariant, purity/determinism, and — the load-bearing one — that the
vol-target scaling is EX-ANTE (extending the series with future dates does not
change past weights).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src import config, signals


def _synthetic(days: int = 800, seed: int = 0) -> pd.DataFrame:
    """Two instruments over ~3 years of business days (no holidays)."""
    idx = pd.bdate_range("2016-01-01", periods=days)
    rng = np.random.default_rng(seed)
    a = 100 * np.cumprod(1 + rng.normal(0.0003, 0.01, days))
    b = 100 * np.cumprod(1 + rng.normal(0.0002, 0.012, days))
    return pd.DataFrame({"A": a, "B": b}, index=idx)


def test_shape_purity_determinism():
    prices = _synthetic()
    snap = prices.copy()
    w1 = signals.tom_seasonal(prices)
    w2 = signals.tom_seasonal(prices)
    assert list(w1.columns) == list(prices.columns)
    assert w1.index.equals(prices.index)
    assert prices.equals(snap), "must not mutate input"
    assert w1.equals(w2), "must be deterministic"


def test_long_only():
    w = signals.tom_seasonal(_synthetic())
    assert (w.to_numpy() >= -1e-12).all(), "TOM is long-only; no negative weights"


def test_active_only_in_tom_window():
    prices = _synthetic()
    w = signals.tom_seasonal(prices)
    active = w.abs().sum(axis=1) > 0
    # ~4 of ~21.5 business days per month.
    assert 0.13 <= active.mean() <= 0.24, f"expected ~0.19 active, got {active.mean():.3f}"
    # Every active day must be in the first-3 or last-1 trading day of its month.
    mask = signals._tom_mask(prices.index)
    assert (active[active].index.isin(mask[mask].index)).all()


def test_exposure_invariant():
    w = signals.tom_seasonal(_synthetic())
    assert w.abs().sum(axis=1).max() <= config.MAX_GROSS_EXPOSURE + 1e-9
    signals.validate_weights(w)


def test_scaling_is_ex_ante():
    """Extending the series with FUTURE dates must not change past weights."""
    full = _synthetic(days=800)
    truncated = full.iloc[:520]
    w_trunc = signals.tom_seasonal(truncated)
    w_full = signals.tom_seasonal(full).loc[w_trunc.index]
    pd.testing.assert_frame_equal(w_trunc, w_full, atol=1e-12, rtol=0)


def test_null_uses_same_constructor():
    """The null benchmark shares _long_inverse_vol; a random mask yields conforming,
    long-only weights active only on the masked days."""
    prices = _synthetic()
    rng = np.random.default_rng(1)
    mask = pd.Series(rng.random(len(prices)) < 0.19, index=prices.index)
    w = signals._long_inverse_vol(prices, mask)
    assert (w.to_numpy() >= -1e-12).all()
    active = w.abs().sum(axis=1) > 0
    assert active[active].index.isin(mask[mask].index).all()
    signals.validate_weights(w)
