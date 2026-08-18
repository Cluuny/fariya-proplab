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

import pandas as pd

from src import config

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
