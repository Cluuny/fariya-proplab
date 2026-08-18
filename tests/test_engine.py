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


def test_buy_and_hold_no_recurring_turnover_cost():
    # Buy&hold no rota tras la entrada → sin costo de TURNOVER recurrente. Con
    # swap=0 el único costo es la entrada; el swap (recurrente) se prueba aparte.
    prices = _series_with_known_sharpe(0.0005, 0.01, n=300)
    w = signals.buy_and_hold(prices)
    costs = {"SPX500": config.CostModel(spread=0.001, slippage=0.0005, swap=0.0)}

    net = engine.backtest(prices, w, costs=costs)
    gross = engine.backtest(prices, w, apply_costs=False)

    diff = (gross - net)
    assert diff.iloc[0] > 0                              # la entrada cobra costo
    assert np.allclose(diff.iloc[1:].to_numpy(), 0.0)    # sin turnover recurrente


def test_buy_and_hold_incurs_recurring_swap():
    # Con swap > 0, buy&hold SÍ incurre un costo diario de mantener (recurrente).
    prices = _series_with_known_sharpe(0.0005, 0.01, n=300)
    w = signals.buy_and_hold(prices)
    costs = {"SPX500": config.CostModel(spread=0.0, slippage=0.0, swap=0.0002)}
    net = engine.backtest(prices, w, costs=costs)
    gross = engine.backtest(prices, w, apply_costs=False)
    diff = (gross - net)
    assert (diff.iloc[2:] > 0).all()                     # swap recurrente cada día


def test_sharpe_annualizes_with_observed_bars_per_year():
    # Dos series con distinto calendario se anualizan cada una con su conteo.
    idx_daily = pd.bdate_range("2020-01-01", periods=520)   # ~260/año
    idx_sparse = pd.bdate_range("2020-01-01", periods=520, freq="2B")  # ~130/año
    r = np.full(520, 0.001)
    s_daily = engine.sharpe(pd.Series(r, index=idx_daily))
    s_sparse = engine.sharpe(pd.Series(r, index=idx_sparse))
    # Mismo retorno/σ por barra pero distinto calendario → distinta anualización.
    assert engine.bars_per_year(pd.Series(r, index=idx_daily)) > 200
    assert engine.bars_per_year(pd.Series(r, index=idx_sparse)) < 160
    assert s_daily > s_sparse


def test_swap_scales_with_days_held():
    dates = pd.bdate_range("2020-01-01", periods=60)
    prices = pd.DataFrame({"X": np.full(60, 100.0)}, index=dates)  # sin movimiento
    w = pd.DataFrame({"X": np.ones(60)}, index=dates)               # mantiene 1.0
    costs = {"X": config.CostModel(spread=0, slippage=0, swap=0.001)}
    net = engine.backtest(prices, w, costs=costs)
    # Sin retorno ni turnover tras la entrada: la pérdida es puro swap diario.
    assert net.iloc[1:].sum() < 0                       # swap acumula (negativo)
    assert np.allclose(net.iloc[2:].to_numpy(), -0.001) # -swap por día mantenido
