"""signals.py — Signal contract (the boundary with Flow 2).

A signal is a PURE FUNCTION: it takes prices (and optionally parameters) and
returns a date-indexed DataFrame of target weights, one column per instrument.
Stateless, no I/O, does not mutate inputs; deterministic.

Exposure invariant: on every date, sum(|weights|) <= 1.

This contract is what lets the future Flow 2 generate code that plugs directly
into the engine. Each strategy is ~20 lines and testable in isolation.
"""

from __future__ import annotations

from typing import Protocol

import numpy as np
import pandas as pd

from src import config
from src import engine

# Numerical tolerance for the exposure invariant.
_EXPOSURE_TOL = 1e-9


class Signal(Protocol):
    """Contract of a pure signal function."""

    def __call__(self, prices: pd.DataFrame, /, **params) -> pd.DataFrame:
        """prices -> target weights (index = dates, columns = instruments)."""
        ...


def check_exposure(
    weights: pd.DataFrame,
    max_gross: float = config.MAX_GROSS_EXPOSURE,
    tol: float = _EXPOSURE_TOL,
) -> pd.Index:
    """Dates where sum(|weights|) exceeds `max_gross` (empty if conforming).

    The cap is `max_gross` (default from config), not a hard 1: inverse-vol
    sizing runs 2-4× gross naturally; absolute risk is controlled downstream.
    """
    gross = weights.abs().sum(axis=1)
    return weights.index[gross > max_gross + tol]


def validate_weights(
    weights: pd.DataFrame,
    max_gross: float = config.MAX_GROSS_EXPOSURE,
    tol: float = _EXPOSURE_TOL,
) -> None:
    """Validate the exposure invariant; raises ValueError if violated."""
    bad = check_exposure(weights, max_gross, tol)
    if len(bad):
        raise ValueError(
            f"Exposición > {max_gross} en {len(bad)} fecha(s): {list(bad[:5])}"
            + (" …" if len(bad) > 5 else "")
        )


def _return_over_calendar(prices: pd.DataFrame, months: int) -> pd.DataFrame:
    """Return over `months` CALENDAR months per instrument, gap-safe.

    For each date, the past price is the last available price on or before
    (date - `months` calendar months) — NOT a fixed number of bars (the paper's
    lookback is in months; 252 bars != 12 months when calendars differ). Uses
    each instrument's own quoting calendar via forward-fill.
    """
    out = {}
    for col in prices.columns:
        s = prices[col].dropna()
        # Price `months` calendar months before each of s's own dates.
        past = s.reindex(s.index - pd.DateOffset(months=months), method="ffill")
        past.index = s.index  # realign to the current dates
        out[col] = (s / past - 1.0).reindex(prices.index)
    return pd.DataFrame(out, index=prices.index)


def tsmom(
    prices: pd.DataFrame,
    /,
    *,
    lookback_months: int = 12,
    vol_window: int = 63,
    vol_target: float = 0.08,
    max_gross: float = config.MAX_GROSS_EXPOSURE,
    rebalance: str = "BMS",
) -> pd.DataFrame:
    """Time-Series Momentum (H001), pure signal conforming to the contract.

    Direction = sign of the `lookback_months`-calendar-month return per
    instrument (long if > 0, short if < 0). Size = inverse-vol (gap-safe
    `engine.rolling_vol`) scaled EX-ANTE to a ~`vol_target` PORTFOLIO vol, capped
    at `max_gross` gross. Rebalanced monthly (`rebalance`, default first business
    day of the month), holding weights between rebalances.

    Ex-ante scaling resolves in ONE step (no convergence loop): build the
    UNSCALED inverse-vol portfolio return, estimate its rolling vol shifted one
    day (only info up to t-1), and divide the target by it. See
    hypotheses/H001_tsmom.yaml (frozen contract).
    """
    if prices.shape[1] == 0:
        return pd.DataFrame(index=prices.index.copy())

    # 1) Direction: sign of the 12-month calendar return.
    direction = np.sign(_return_over_calendar(prices, lookback_months))

    # 2) Relative inverse-vol weights (gap-safe vol on own trading days).
    vol = engine.rolling_vol(prices, vol_window)
    raw = direction / vol.replace(0.0, np.nan)
    raw = raw.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    gross_raw = raw.abs().sum(axis=1)
    rel = raw.div(gross_raw.where(gross_raw > 0, np.nan), axis=0).fillna(0.0)

    # 3) Ex-ante portfolio-vol scalar (one step, shifted to use only info <= t-1).
    asset_ret = engine._asset_returns(prices)
    port_ret = (rel.shift(1).fillna(0.0) * asset_ret).sum(axis=1)
    ann = np.sqrt(engine.bars_per_year(port_ret))
    port_vol = (port_ret.rolling(vol_window).std() * ann).shift(1)
    scalar = (vol_target / port_vol).replace([np.inf, -np.inf], np.nan)

    weights = rel.mul(scalar, axis=0)

    # 4) Cap gross exposure: clip the per-date scalar so sum(|w|) <= max_gross.
    gross = weights.abs().sum(axis=1)
    over = gross > max_gross
    if over.any():
        clip = pd.Series(1.0, index=weights.index)
        clip[over] = max_gross / gross[over]
        weights = weights.mul(clip, axis=0)
    weights = weights.fillna(0.0)

    # 5) Monthly rebalance with holding: sample on rebalance dates, ffill between.
    reb_dates = pd.date_range(prices.index.min(), prices.index.max(), freq=rebalance)
    reb_on_frame = weights.reindex(reb_dates, method="ffill")
    out = reb_on_frame.reindex(prices.index, method="ffill").fillna(0.0)
    return out


def buy_and_hold(prices: pd.DataFrame, /, *, weight: float = 1.0) -> pd.DataFrame:
    """Reference signal: constant exposure, split across instruments.

    Pure function conforming to the contract: holds `weight` of total gross
    exposure, split equally across the columns of `prices`, constant over time.
    Does not mutate `prices`.
    """
    n = prices.shape[1]
    if n == 0:
        return pd.DataFrame(index=prices.index.copy())
    per = weight / n
    weights = pd.DataFrame(per, index=prices.index.copy(), columns=list(prices.columns))
    return weights
