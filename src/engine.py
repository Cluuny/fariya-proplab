"""engine.py — Backtest engine.

Translates target weights into NET returns by applying costs. It is the ONLY
module in the system that applies costs (commission, spread, slippage, impact).

No-look-ahead convention: weights decided at the close of day t-1 capture the
asset return of day t. The rotation cost is charged on the day the weight
changes; the initial entry (from 0 to the first weight) is charged on day 0.

Determinism: same inputs (weights, prices, costs) -> same returns.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src import config


def _asset_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Simple per-asset returns (pct_change), first row = 0.

    Sanitizes non-finite values: a zero/non-positive price (an anomaly that
    loaders flags but does not correct) would produce ±inf; it is neutralized
    to 0.0 so that a single corrupt tick does not propagate inf across the whole
    backtest and report.
    """
    ret = prices.pct_change()
    return ret.replace([np.inf, -np.inf], np.nan).fillna(0.0)


def _cost_rate(instrument: str, costs: dict[str, config.CostModel]) -> float:
    """Total cost per unit of rotated weight for an instrument."""
    cm = costs.get(instrument, config.DEFAULT_COST)
    return cm.spread + cm.slippage + cm.impact + cm.commission


def backtest(
    prices: pd.DataFrame,
    weights: pd.DataFrame,
    *,
    costs: dict[str, config.CostModel] | None = None,
    apply_costs: bool = True,
) -> pd.Series:
    """Return the strategy's net return series.

    - `prices`: per-instrument prices (columns), indexed by date.
    - `weights`: target weights aligned to `prices` (same columns).
    - `costs`: per-instrument cost model; defaults to `config.COSTS`.
    - `apply_costs=False`: returns GROSS returns (for comparison/tests).
    """
    if costs is None:
        costs = config.COSTS

    # Align weights to the price columns/index.
    w = weights.reindex(index=prices.index, columns=prices.columns).fillna(0.0)
    asset_ret = _asset_returns(prices)

    # Gross return: previous day's weights · today's asset return.
    gross = (w.shift(1).fillna(0.0) * asset_ret).sum(axis=1)

    if not apply_costs:
        return gross.rename("return")

    # Per-instrument turnover: |w_t - w_{t-1}|, with w_{-1}=0 (initial entry).
    turnover = (w - w.shift(1).fillna(0.0)).abs()
    rates = pd.Series({col: _cost_rate(str(col), costs) for col in w.columns})
    turnover_cost = turnover.mul(rates, axis=1).sum(axis=1)

    # Swap/carry: DAILY charge proportional to |weight| held (the previous day's
    # weight earns today's return, so it is the position held). Not turnover.
    swap_rates = pd.Series(
        {col: costs.get(str(col), config.DEFAULT_COST).swap for col in w.columns}
    )
    swap_cost = w.shift(1).fillna(0.0).abs().mul(swap_rates, axis=1).sum(axis=1)

    net = gross - turnover_cost - swap_cost
    return net.rename("return")


def bars_per_year(returns: pd.Series) -> float:
    """Observed bars per year of a datetime-indexed series.

    Different calendars (FX ~260/year, indices ~247/year after dropping weekend
    bars) must each be annualized with their OWN count, not a global constant, to
    avoid a systematic Sharpe bias.
    """
    idx = returns.dropna().index
    if len(idx) < 2 or not isinstance(idx, pd.DatetimeIndex):
        return float(config.TRADING_DAYS_PER_YEAR)
    years = (idx[-1] - idx[0]).days / 365.25
    return len(idx) / years if years > 0 else float(config.TRADING_DAYS_PER_YEAR)


def sharpe(returns: pd.Series, *, periods_per_year: float | None = None) -> float:
    """Annualized Sharpe (risk-free rate = 0).

    If `periods_per_year` is None, it is inferred from the series' observed
    calendar (`bars_per_year`); pass a value to override (e.g. for synthetic
    arrays without dates, where it defaults to 252).
    """
    r = returns.dropna()
    sd = r.std(ddof=0)
    if sd == 0 or np.isnan(sd):
        return 0.0
    ppy = bars_per_year(r) if periods_per_year is None else periods_per_year
    return float(np.sqrt(ppy) * r.mean() / sd)
