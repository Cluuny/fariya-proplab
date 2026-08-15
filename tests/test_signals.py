"""Section 3 — signal-contract: pureza/determinismo, forma de salida,
invariante de exposición y señal de referencia buy & hold."""

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
    pd.testing.assert_frame_equal(prices, snapshot)  # entradas intactas


def test_output_shape(prices):
    w = signals.buy_and_hold(prices)
    assert list(w.index) == list(prices.index)
    assert list(w.columns) == list(prices.columns)


def test_buy_and_hold_constant_and_conforming(prices):
    w = signals.buy_and_hold(prices)
    # Pesos constantes en el tiempo.
    assert (w.nunique() == 1).all()
    # Invariante de exposición.
    signals.validate_weights(w)
    assert len(signals.check_exposure(w)) == 0


def test_exposure_violation_detected(prices):
    bad = pd.DataFrame(0.6, index=prices.index, columns=prices.columns[:2])  # suma=1.2
    offending = signals.check_exposure(bad)
    assert len(offending) == len(prices.index)
    with pytest.raises(ValueError):
        signals.validate_weights(bad)


def test_exposure_conforming_accepted(prices):
    ok = pd.DataFrame(0.3, index=prices.index, columns=prices.columns[:2])  # suma=0.6
    signals.validate_weights(ok)  # no lanza
