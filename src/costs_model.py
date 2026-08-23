"""costs_model.py — the cost floor as a DECISION TOOL (Bloque A).

Four measurements (H001-A/B, H007-A/B) put gross Sharpe at 0.23-0.37 and show costs
eat ~88% of the gross return. This turns that into a pre-trade screen: given a
hypothesis's expected gross, turnover and holding, what gross Sharpe does it NEED to
clear the falsifier — and does the literature support that?

Cost decomposition (annual, as fraction of NAV), calibrated to the measured runs:
  margin  = swap_margin_daily · gross · TRADING_DAYS        (per unit of GROSS/day)
  spread  = (spread+slippage) · turnover_annual             (per unit of TURNOVER)
  carry   = E[carry·w]  (signed; small for trend, ~+0.2%/yr; 0 by default here)
Verified: gross 1.71, turnover 8.8 → margin 1.96% + spread 0.13% − carry 0.19%
  = ~1.9% cost vs ~2.16% gross (Sharpe ~0.03 net at 8% vol). Margin is ~92% of it.
"""

from __future__ import annotations

from dataclasses import dataclass

from src import config

# Per-unit rates (fractions), from config's calibrated cost model.
MARGIN_DAILY_FX = config._MARGIN_FX * config.BROKER_MARGIN_MULT * config.TRADING_DAY_SWAP_FACTOR  # ~0.42 bp/día
SPREAD_PER_TURNOVER = config.DEFAULT_COST.spread + config.DEFAULT_COST.slippage  # ~1.5 bp/rotación
TRADING_DAYS = 261  # sesiones FX/año observadas (el margen ya lleva el factor 365/261)


@dataclass(frozen=True)
class CostBreakdown:
    margin: float        # %/año por el margen (gross × días)
    spread: float        # %/año por spread+slippage (turnover)
    carry: float         # %/año de ingreso por carry (signed)
    total: float         # coste neto anual (%/año)


def annual_cost(gross: float, turnover: float, *, carry_income: float = 0.0,
                margin_daily: float = MARGIN_DAILY_FX,
                spread_per_turnover: float = SPREAD_PER_TURNOVER,
                trading_days: int = TRADING_DAYS) -> CostBreakdown:
    """Annual cost (fraction of NAV) for a strategy at a given gross and turnover.

    `gross` = mean |weights| sum; `turnover` = annual sum |Δw|; `carry_income` =
    E[carry·w] annualized (fraction, default 0 = don't credit carry).
    """
    margin = margin_daily * gross * trading_days
    spread = spread_per_turnover * turnover
    total = margin + spread - carry_income
    return CostBreakdown(margin=margin, spread=spread, carry=carry_income, total=total)


def sharpe_bruto_requerido(vol_objetivo: float, gross: float, turnover: float,
                           umbral: float = 0.4, *, carry_income: float = 0.0) -> float:
    """Minimum GROSS Sharpe to reach a net Sharpe of `umbral`.

    net_sharpe = gross_sharpe − cost/vol → required gross = umbral + cost/vol.
    The `umbral=0` case gives the break-even gross Sharpe.
    """
    cost = annual_cost(gross, turnover, carry_income=carry_income).total
    return umbral + cost / vol_objetivo


def break_even(vol_objetivo: float, gross: float, turnover: float, **kw) -> float:
    """Gross Sharpe at which net = 0."""
    return sharpe_bruto_requerido(vol_objetivo, gross, turnover, umbral=0.0, **kw)


# Break-even gross Sharpe at 100% duty (margin cost / vol at gross ~1.7, vol 8%).
BREAKEVEN_FULL_DUTY = 0.24


def sharpe_bruto_requerido_duty(duty_cycle: float, umbral: float = 0.40,
                                breakeven_full: float = BREAKEVEN_FULL_DUTY) -> float:
    """Required WHOLE-SERIES gross Sharpe as a function of DUTY CYCLE.

        requerido ≈ breakeven_full × duty_cycle + umbral      (0.24·duty + 0.40)

    The margin is paid only on days with a position, so the break-even scales with
    the duty cycle: duty 100% → 0.64, 50% → 0.52, 20% → 0.45, 10% → 0.42.

    TRAMPA (documentar): el bruto de una estrategia de duty bajo se mide sobre TODA
    la serie, incluidos los días flat. Un efecto grande en sus 20 días/año se DILUYE
    al anualizar: el Sharpe whole-series ≈ Sharpe_activo × √duty (la media ∝ duty, la
    desv. ∝ √duty). Así que para cumplir `requerido` con duty bajo hace falta un
    Sharpe del período ACTIVO alto: `activo ≥ (0.24·duty + 0.40)/√duty`. El ahorro de
    margen es real (break-even baja lineal) pero la dilución (√duty) NO es magia:
    parcialmente se compensan. duty bajo ayuda, pero exige un edge activo fuerte.
    """
    return breakeven_full * duty_cycle + umbral
