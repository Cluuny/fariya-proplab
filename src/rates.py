"""rates.py — historical policy rates → time-varying carry matrix.

The swap `carry` (signed rate differential a long earns) must use HISTORICAL rates,
not a 2026 snapshot: the differential — and its SIGN — moved a lot over 2003-2026
(EURUSD carry was positive in 2009-2015 when EUR>USD). Uses BIS monthly central-bank
policy rates (WS_CBPOL) cached in data/rates/policy_rates.csv, reindexed to daily.

`carry_matrix(index, instruments)` returns a date×instrument DataFrame of the daily
carry a LONG earns (fraction/day), including the 365/261 trading-day convention
factor. The engine applies it as `swap_cost = swap_margin·|w| − carry·w`.
"""

from __future__ import annotations

import functools

import pandas as pd

from src import config


@functools.lru_cache(maxsize=1)
def _monthly_rates() -> pd.DataFrame:
    """BIS monthly policy rates (% annual), month-indexed, gaps filled."""
    df = pd.read_csv(config.DATA_RATES)
    df["month"] = pd.to_datetime(df["month"])
    df = df.set_index("month").sort_index()
    # JPY starts 2006, CHF has gaps → ffill then bfill (early rates were ~flat/low).
    return df.ffill().bfill()


def daily_policy_rates(index: pd.DatetimeIndex) -> pd.DataFrame:
    """Policy rates (% annual) per currency, reindexed to `index` (ffill from the
    most recent month; bfill for any dates before the first month)."""
    monthly = _monthly_rates()
    idx = pd.DatetimeIndex(index)
    combined = monthly.reindex(monthly.index.union(idx)).ffill().bfill()
    return combined.reindex(idx)


def carry_matrix(index: pd.DatetimeIndex, instruments: list[str]) -> pd.DataFrame:
    """Daily carry a LONG earns (fraction/day), date×instrument, historical.

    FX: (r_base − r_quote); metals: −r_USD; indices: (div_yield − r_local).
    Scaled by 1/100/360 × TRADING_DAY_SWAP_FACTOR (365/261) to a per-session value.
    """
    r = daily_policy_rates(index)
    f = config.TRADING_DAY_SWAP_FACTOR / 100.0 / 360.0
    out = {}
    for sym in instruments:
        if sym in config._FX_LEGS:
            base, quote = config._FX_LEGS[sym]
            d = r[base] - r[quote]
        elif sym in ("XAUUSD", "XAGUSD"):
            d = -r["USD"]
        elif sym in config._DIV_YIELD:
            d = config._DIV_YIELD[sym] - r[config._INDEX_CCY[sym]]
        else:
            d = pd.Series(0.0, index=index)
        out[sym] = d * f
    return pd.DataFrame(out, index=index)
