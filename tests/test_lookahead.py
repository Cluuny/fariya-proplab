"""Look-ahead guard — the signal-layer equivalent of the closed-form check.

Verifies the engine's no-look-ahead convention (`w_{t-1}·ret_t`) end to end:
- a signal that PEEKS at tomorrow's return must produce an absurd Sharpe;
- a signal that only looks at the past must produce a modest one.
If the first is not huge, the shift is broken in the direction that HIDES the
bug. If the second is huge, there is look-ahead. This is the trap that nine
instruments across three calendars set for a backtest, so it exists before any
hypothesis with a result we might like.
"""

import numpy as np
import pandas as pd

from src import engine


def _synthetic_prices(n=3000, seed=0):
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2005-01-03", periods=n)
    data = {}
    for i, sym in enumerate(("A", "B")):
        rets = rng.normal(0.0, 0.01, n)
        data[sym] = 100 * np.cumprod(1 + rets)
    return pd.DataFrame(data, index=dates)


def test_lookahead_guard():
    prices = _synthetic_prices()
    asset_returns = prices.pct_change()

    # Cheating signal: weight = sign of TOMORROW's return (peeks at the future).
    # With w_{t-1}·ret_t the position earns |ret_t| every day → absurd Sharpe.
    cheat = np.sign(asset_returns.shift(-1)).fillna(0.0)
    s_cheat = engine.sharpe(engine.backtest(prices, cheat, apply_costs=False))
    assert s_cheat > 5, f"look-ahead cheat Sharpe {s_cheat:.2f} not huge → shift oculta el bug"

    # Honest signal: weight = sign of YESTERDAY's return (past only). Modest.
    honest = np.sign(asset_returns.shift(1)).fillna(0.0)
    s_honest = engine.sharpe(engine.backtest(prices, honest, apply_costs=False))
    assert s_honest < 2, f"honest Sharpe {s_honest:.2f} demasiado alto → hay look-ahead"
