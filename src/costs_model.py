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

    Este es el requerido de la SERIE COMPLETA. NO es el número de decisión para una
    estrategia de duty bajo: ver sharpe_activo_requerido — bajar el duty SUBE el
    listón en términos de señal activa, no lo baja.
    """
    return breakeven_full * duty_cycle + umbral


def sharpe_activo_requerido(duty_cycle: float) -> float:
    """Sharpe del PERÍODO ACTIVO requerido para cumplir el umbral, a un duty dado.

        Sharpe_activo ≈ 0.40/√duty + 0.245
        duty 100% → 0.645 · 50% → 0.81 · 20% → 1.14 · 10% → 1.51

    CLAVE (corrige un error previo): bajar el duty cycle SUBE este listón, no lo baja.
    El bruto de la serie completa se DILUYE sobre los días flat (`Sharpe_whole ≈
    Sharpe_activo·√duty`: media ∝ duty, desv. ∝ √duty), y ese término (0.40/√duty)
    domina al ahorro de margen (~constante 0.245). El requerido de serie completa
    (0.24·duty+0.40) baja con el duty, pero el ALCANZABLE se diluye igual → lo que
    importa es el Sharpe ACTIVO, que sube. Duty bajo NO baja el coste efectivo del
    edge; el argumento de COT es la INFORMACIÓN no-de-precio, no un listón más bajo.
    """
    return 0.40 / (duty_cycle ** 0.5) + 0.245


# ============================================================================
# INTRADÍA — el suelo de costes cambia de régimen: lo domina el ROTAR, no el
# mantener. El modelo swing de arriba (margen diario) no aplica; el coste es
# comisión + spread por operación × frecuencia.
# ============================================================================

TRADING_DAYS_INTRADAY = 252  # sesiones/año (convención estándar intradía)

# Specs CONTRACTUALES de CME (tick/point value son definiciones del contrato, estables)
# + comisión IBKR ~$4.20 round-trip all-in (interactivebrokers.com, ya citado en
# docs/futures_case.md). `notional_usd` SÍ depende del nivel de precio → se fija a un
# nivel declarado (2026-08, orden de magnitud; RECALCULAR a precio corriente antes de
# usar en decisión real). `spread_ticks` = ancho típico del front (1 tick en ES/NQ/GC/CL).
CONTRACT_SPECS = {
    #        tick_usd  notional_usd  comision_rt  spread_ticks   (nivel de precio asumido)
    "ES": {"tick_usd": 12.50, "notional_usd": 300_000, "comision_rt": 4.20, "spread_ticks": 1},  # ES~6000×$50
    "NQ": {"tick_usd":  5.00, "notional_usd": 400_000, "comision_rt": 4.20, "spread_ticks": 1},  # NQ~20000×$20
    "CL": {"tick_usd": 10.00, "notional_usd":  75_000, "comision_rt": 4.20, "spread_ticks": 1},  # CL~$75×1000
    "GC": {"tick_usd": 10.00, "notional_usd": 240_000, "comision_rt": 4.20, "spread_ticks": 1},  # GC~$2400×100
}


def costo_anual_intraday(trades_por_dia: float, contrato: str = "ES", *,
                         trading_days: int = TRADING_DAYS_INTRADAY,
                         specs: dict | None = None) -> float:
    """Coste anual (fracción del notional) de rotar `trades_por_dia` veces al día.

        costo_anual = trades_por_dia · trading_days · (comision_rt + spread_$) / notional

    `trades_por_dia` cuenta ROUND-TRIPS (por eso se usa la comisión round-trip). El
    `spread_$` es el coste de cruzar el spread una vez por round-trip (1 tick en el
    front líquido). El mantener (margen) es despreciable en intradía → se omite.
    """
    sp = specs if specs is not None else CONTRACT_SPECS.get(contrato)
    if sp is None:
        raise ValueError(f"contrato desconocido: {contrato!r} (usa {list(CONTRACT_SPECS)} o pasa specs=)")
    spread_usd = sp["spread_ticks"] * sp["tick_usd"]
    costo_por_rt = sp["comision_rt"] + spread_usd
    return trades_por_dia * trading_days * costo_por_rt / sp["notional_usd"]


def sharpe_bruto_requerido_intraday(trades_por_dia: float, contrato: str = "ES", *,
                                    umbral: float = 0.40, vol_objetivo: float = 0.08,
                                    trading_days: int = TRADING_DAYS_INTRADAY,
                                    specs: dict | None = None) -> float:
    """Bruto Sharpe requerido para netear `umbral`, en régimen INTRADÍA.

        bruto_requerido = umbral + costo_anual_intraday / vol_objetivo

    Nota de vehículo: el intradía de microestructura sólo tiene sentido en FUTUROS
    (el spot/CFD no tiene volumen consolidado ni cinta); el `contrato` ES/NQ/CL/GC
    parametriza el suelo, como el `vehiculo` parametriza el suelo swing.
    """
    costo = costo_anual_intraday(trades_por_dia, contrato,
                                 trading_days=trading_days, specs=specs)
    return umbral + costo / vol_objetivo


def trades_por_dia_break_1p96(contrato: str = "ES", *, specs: dict | None = None,
                              trading_days: int = TRADING_DAYS_INTRADAY) -> float:
    """A cuántos round-trips/día el coste intradía IGUALA el 1.96%/año del margen CFD
    (el suelo que mató seis hipótesis). Por encima de esto, intradía es MÁS caro que
    el swing en CFD. Es la advertencia principal de la tabla."""
    por_trade_dia = costo_anual_intraday(1.0, contrato, trading_days=trading_days, specs=specs)
    return 0.0196 / por_trade_dia
