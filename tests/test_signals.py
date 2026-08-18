"""Section 3 — signal-contract: purity/determinism, output shape,
exposure invariant and buy & hold reference signal."""

import numpy as np
import pandas as pd
import pytest

from src import signals


@pytest.fixture
def prices():
    dates = pd.bdate_range("2020-01-01", periods=30)
    rng = np.random.default_rng(0)
    data = {
        sym: 100 * np.exp(np.cumsum(rng.normal(0, 0.01, len(dates))))
        for sym in ("EURUSD", "GBPUSD", "USDJPY")
    }
    return pd.DataFrame(data, index=dates)


def test_determinism_and_no_mutation(prices):
    snapshot = prices.copy(deep=True)
    w1 = signals.buy_and_hold(prices)
    w2 = signals.buy_and_hold(prices)
    pd.testing.assert_frame_equal(w1, w2)
    pd.testing.assert_frame_equal(prices, snapshot)  # inputs intact


def test_output_shape(prices):
    w = signals.buy_and_hold(prices)
    assert list(w.index) == list(prices.index)
    assert list(w.columns) == list(prices.columns)


def test_buy_and_hold_constant_and_conforming(prices):
    w = signals.buy_and_hold(prices)
    # Weights constant over time.
    assert (w.nunique() == 1).all()
    # Exposure invariant.
    signals.validate_weights(w)
    assert len(signals.check_exposure(w)) == 0


def test_exposure_violation_detected(prices):
    # Excede MAX_GROSS_EXPOSURE (4): 3 columnas × 2.0 = 6.0 > 4.
    bad = pd.DataFrame(2.0, index=prices.index, columns=prices.columns[:3])  # sum=6.0
    offending = signals.check_exposure(bad)
    assert len(offending) == len(prices.index)
    with pytest.raises(ValueError):
        signals.validate_weights(bad)


def test_exposure_conforming_accepted(prices):
    ok = pd.DataFrame(0.3, index=prices.index, columns=prices.columns[:2])  # sum=0.6
    signals.validate_weights(ok)  # does not raise


def test_max_gross_allows_inverse_vol_and_rejects_above_cap():
    from src import config
    dates = pd.bdate_range("2020-01-01", periods=10)
    cols = ["A", "B", "C"]
    # Bruto 3× (típico de vol-inversa) — conforme si <= MAX_GROSS_EXPOSURE (4).
    ok = pd.DataFrame(1.0, index=dates, columns=cols)          # suma |w| = 3
    signals.validate_weights(ok)                               # no lanza
    assert len(signals.check_exposure(ok)) == 0
    # Por encima del tope → falla.
    over = pd.DataFrame(config.MAX_GROSS_EXPOSURE, index=dates, columns=cols)
    assert len(signals.check_exposure(over)) == len(dates)
