"""Section 4 — backtest-engine: reproduction of a known Sharpe,
determinism, and the effect of costs."""

import numpy as np
import pandas as pd

from src import config, engine, signals


def _series_with_known_sharpe(mu_daily, sigma_daily, n=2000, seed=7):
    """Build prices whose simple returns have ~known mean/σ."""
    rng = np.random.default_rng(seed)
    rets = rng.normal(mu_daily, sigma_daily, n)
    dates = pd.bdate_range("2005-01-03", periods=n)
    prices = pd.DataFrame(
        {"SPX500": 1000 * np.cumprod(1 + rets)}, index=dates
    )
    return prices


def test_buy_and_hold_reproduces_known_sharpe():
    # The series' "known Sharpe" is the Sharpe of its own returns. A correct
    # engine reproduces that number when running buy & hold (the engine must not
    # distort the Sharpe of the underlying). This isolates the engine's
    # correctness from the sampling noise of the generating process.
    prices = _series_with_known_sharpe(0.0004, 0.01, n=4000)
    reference = engine.sharpe(prices["SPX500"].pct_change().dropna())

    w = signals.buy_and_hold(prices)
    net = engine.backtest(prices, w)  # buy&hold: no recurring costs
    got = engine.sharpe(net)

    assert abs(got - reference) <= config.SHARPE_REFERENCE.tolerance


def test_nonpositive_price_does_not_produce_inf():
    # A zero price (an anomaly flagged by loaders) must NOT generate inf returns
    # that poison the backtest. Regression found in the E2E.
    dates = pd.bdate_range("2020-01-01", periods=10)
    prices = pd.DataFrame({"X": np.full(10, 100.0)}, index=dates)
    prices.iloc[5, 0] = 0.0
    w = signals.buy_and_hold(prices)
    net = engine.backtest(prices, w)
    assert np.isfinite(net.to_numpy()).all()


def test_deterministic():
    prices = _series_with_known_sharpe(0.0003, 0.012, n=500)
    w = signals.buy_and_hold(prices)
    r1 = engine.backtest(prices, w)
    r2 = engine.backtest(prices, w)
    pd.testing.assert_series_equal(r1, r2)


def test_costs_reduce_return_when_rotating():
    prices = _series_with_known_sharpe(0.0005, 0.01, n=300)
    # Rotating strategy: alternates 0/1 exposure on a single instrument.
    w = pd.DataFrame(
        {"SPX500": [float(i % 2) for i in range(len(prices))]}, index=prices.index
    )
    costs = {"SPX500": config.CostModel(spread=0.001, slippage=0.0005)}
    gross = engine.backtest(prices, w, apply_costs=False).sum()
    net = engine.backtest(prices, w, costs=costs).sum()
    assert net < gross


def test_buy_and_hold_no_recurring_costs():
    prices = _series_with_known_sharpe(0.0005, 0.01, n=300)
    w = signals.buy_and_hold(prices)
    costs = {"SPX500": config.CostModel(spread=0.001, slippage=0.0005)}

    net = engine.backtest(prices, w, costs=costs)
    gross = engine.backtest(prices, w, apply_costs=False)

    # They only differ on the entry day (t=0); afterwards, zero cost.
    diff = (gross - net)
    assert diff.iloc[0] > 0            # initial entry charges a cost
    assert np.allclose(diff.iloc[1:].to_numpy(), 0.0)  # no recurring costs
