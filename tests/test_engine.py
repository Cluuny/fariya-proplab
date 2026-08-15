"""Section 4 — backtest-engine: reproducción de un Sharpe conocido,
determinismo, y efecto de los costos."""

import numpy as np
import pandas as pd

from src import config, engine, signals


def _series_with_known_sharpe(mu_daily, sigma_daily, n=2000, seed=7):
    """Construye precios cuyos retornos simples tienen media/σ ~ conocidas."""
    rng = np.random.default_rng(seed)
    rets = rng.normal(mu_daily, sigma_daily, n)
    dates = pd.bdate_range("2005-01-03", periods=n)
    prices = pd.DataFrame(
        {"SPX500": 1000 * np.cumprod(1 + rets)}, index=dates
    )
    return prices


def test_buy_and_hold_reproduces_known_sharpe():
    # El "Sharpe conocido" de la serie es el Sharpe de sus propios retornos.
    # Un motor correcto reproduce ese número al correr buy & hold (el motor no
    # debe distorsionar el Sharpe del subyacente). Esto aísla la corrección del
    # motor del ruido de muestreo del proceso generador.
    prices = _series_with_known_sharpe(0.0004, 0.01, n=4000)
    reference = engine.sharpe(prices["SPX500"].pct_change().dropna())

    w = signals.buy_and_hold(prices)
    net = engine.backtest(prices, w)  # buy&hold: sin costos recurrentes
    got = engine.sharpe(net)

    assert abs(got - reference) <= config.SHARPE_REFERENCE.tolerance


def test_nonpositive_price_does_not_produce_inf():
    # Un precio en cero (anomalía marcada por loaders) NO debe generar retornos
    # inf que envenenen el backtest. Regresión encontrada en el E2E.
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
    # Estrategia que rota: alterna exposición 0/1 en un solo instrumento.
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

    # Sólo difieren en el día de entrada (t=0); después, costo cero.
    diff = (gross - net)
    assert diff.iloc[0] > 0            # entrada inicial cobra costo
    assert np.allclose(diff.iloc[1:].to_numpy(), 0.0)  # sin costos recurrentes
