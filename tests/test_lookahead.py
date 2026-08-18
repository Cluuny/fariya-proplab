"""Look-ahead guard — the signal-layer equivalent of the closed-form check.

Verifies the engine's no-look-ahead convention (`w_{t-1}·ret_t`) end to end AND
its handling of MISALIGNED calendars (the real risk: with 9 instruments on 3
calendars, e.g. SPX500 has ~203 business days EURUSD has but it lacks):

- a signal that PEEKS at tomorrow's return must produce an absurd Sharpe;
- a signal that only looks at the past must produce a modest one;
- a return across a calendar gap must NOT be dropped (naive pct_change().fillna(0)
  zeroes both the gap day and the reopen day) NOR forward-filled onto the wrong
  day (subtle look-ahead): it belongs to the reopen day.

The synthetic prices are deliberately MISALIGNED so the test can see the trap a
single aligned bdate_range hides.
"""

import numpy as np
import pandas as pd

from src import engine


def _misaligned_prices(n=3000, seed=0):
    """Two instruments on the same span but DIFFERENT calendars (B has gaps)."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2005-01-03", periods=n)
    data = {
        "A": 100 * np.cumprod(1 + rng.normal(0.0, 0.01, n)),
        "B": 100 * np.cumprod(1 + rng.normal(0.0, 0.01, n)),
    }
    prices = pd.DataFrame(data, index=dates)
    # B does not trade on ~15% of A's days (misaligned calendar → NaN in the union).
    gap_mask = rng.random(n) < 0.15
    prices.loc[prices.index[gap_mask], "B"] = np.nan
    return prices


def test_lookahead_guard_with_misaligned_calendars():
    prices = _misaligned_prices()
    asset_returns = engine._asset_returns(prices)  # gap-safe returns

    # Cheat: weight = sign of TOMORROW's return (peeks). Earns |ret| daily → absurd.
    cheat = np.sign(asset_returns.shift(-1)).fillna(0.0)
    s_cheat = engine.sharpe(engine.backtest(prices, cheat, apply_costs=False))
    assert s_cheat > 5, f"look-ahead cheat Sharpe {s_cheat:.2f} not huge → shift oculta el bug"

    # Honest: weight = sign of YESTERDAY's return (past only). Modest.
    honest = np.sign(asset_returns.shift(1)).fillna(0.0)
    s_honest = engine.sharpe(engine.backtest(prices, honest, apply_costs=False))
    assert s_honest < 2, f"honest Sharpe {s_honest:.2f} demasiado alto → hay look-ahead"


def test_cross_gap_return_not_dropped_and_attributed_to_reopen():
    # Un instrumento con un hueco de calendario: el retorno que cruza el hueco
    # NO se pierde y se atribuye al día de reapertura (no al hueco, no antes).
    dates = pd.bdate_range("2020-01-01", periods=30)
    rng = np.random.default_rng(1)
    b = 100 * np.cumprod(1 + rng.normal(0, 0.01, 30))
    prices = pd.DataFrame({"B": b}, index=dates)
    gap = 5
    prices.iloc[gap, 0] = np.nan  # B no cotizó el día `gap`
    ar = engine._asset_returns(prices)["B"]
    real_gap_ret = b[gap + 1] / b[gap - 1] - 1
    assert ar.iloc[gap] == 0.0                              # hueco → sin movimiento
    assert np.isclose(ar.iloc[gap + 1], real_gap_ret)       # reapertura → retorno real
    # y NO se perdió: la suma de hueco+reapertura es el retorno real cruzado.
    assert np.isclose(ar.iloc[gap] + ar.iloc[gap + 1], real_gap_ret)
