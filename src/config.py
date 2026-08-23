"""Explicit, versioned lab configuration (decision D6).

Everything that affects a measured result lives here, not embedded ad hoc in the
code, so that backtests are reproducible and adjustable.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# --- Paths ---
ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT / "data" / "raw"
DATA_CLEAN = ROOT / "data" / "clean"
DATA_RATES = ROOT / "data" / "rates" / "policy_rates.csv"  # BIS historical policy rates
RESULTS = ROOT / "results"

# --- Universe (master document, section 8.2) ---
# Corrected from the original: NAS100 and UK100 were dropped (four equity indices,
# three highly correlated, no energy, no Asia — the worst mix for a portfolio whose
# whole point is to lower volatility by decorrelation). Replaced by JPN225 (Nikkei,
# Asia) and BRENT (energy) for cross-class / cross-geography diversification.
INSTRUMENTS: tuple[str, ...] = (
    # FX majors (comparten el factor USD)
    "EURUSD",
    "GBPUSD",
    "USDJPY",
    "AUDUSD",
    "USDCAD",
    # FX crosses (decorrelacionan del factor USD) — auditoría Bloque 1
    "EURJPY",
    "GBPJPY",
    "AUDJPY",
    "EURAUD",
    "GBPAUD",
    "EURCHF",
    # Metales
    "XAUUSD",
    "XAGUSD",
    # Índices de renta variable (geográficamente diversos)
    "SPX500",
    "GER40",
    "JPN225",
    "HK50",
)
# US30 (Dow) retirado del universo activo: MISMA exposición que SPX500
# (equity-US, corr ~0.95). En sizing vol-inversa se paga spread dos veces por la
# misma posición — fricción pura sin información nueva (ver change universe-trim-us30
# y docs/breadth-lessons.md). Se conserva su mapeo abajo por si se re-evalúa.
# BRENT retirado del universo activo: cobertura diaria de Dukascopy sparse (~168
# obs/año, ~1421 días hábiles faltantes en 15 años → inusable). Se conserva su
# mapeo abajo; evaluar un símbolo de energía más denso (p. ej. WTI LIGHTCMDUSD)
# antes de re-incluir energía por decorrelación.

# --- Internal symbol → Dukascopy instrument code ---
# Internal names do not match Dukascopy's; every universe instrument MUST have a
# mapping or ingestion fails visibly (never a silently empty/wrong download).
# NOTE: the index/commodity codes are the community-known Dukascopy symbols; they
# are verified against Dukascopy's instrument list at ingestion time.
DUKASCOPY_SYMBOLS: dict[str, str] = {
    "EURUSD": "EURUSD",
    "GBPUSD": "GBPUSD",
    "USDJPY": "USDJPY",
    "AUDUSD": "AUDUSD",
    "USDCAD": "USDCAD",
    "EURJPY": "EURJPY",
    "GBPJPY": "GBPJPY",
    "AUDJPY": "AUDJPY",
    "EURAUD": "EURAUD",
    "GBPAUD": "GBPAUD",
    "EURCHF": "EURCHF",
    "XAUUSD": "XAUUSD",
    "XAGUSD": "XAGUSD",
    "SPX500": "USA500IDXUSD",
    "US30": "USA30IDXUSD",
    "GER40": "DEUIDXEUR",
    "JPN225": "JPNIDXJPY",
    "HK50": "HKGIDXHKD",
    "BRENT": "BRENTCMDUSD",  # retirado del universo activo (auditoría: energía esparsa)
}

# Price scale factor per instrument for the .bi5 integer prices (verified for
# EURUSD = 1e5; the rest are the community-known point values). COSMETIC: returns
# (pct_change) and Sharpe are scale-invariant, so a wrong factor changes only the
# displayed price level, not any downstream metric.
DUKASCOPY_POINT: dict[str, float] = {
    "EURUSD": 1e5, "GBPUSD": 1e5, "AUDUSD": 1e5, "USDCAD": 1e5,
    "EURAUD": 1e5, "GBPAUD": 1e5, "EURCHF": 1e5,
    "USDJPY": 1e3, "EURJPY": 1e3, "GBPJPY": 1e3, "AUDJPY": 1e3,
    "XAUUSD": 1e3, "XAGUSD": 1e3,
    "SPX500": 1e3, "US30": 1e3, "GER40": 1e3, "JPN225": 1e3, "HK50": 1e3, "BRENT": 1e3,
}

# --- Data quality validation ---
# Anomalous return threshold, in standard deviations (document: >5σ).
ANOMALOUS_RETURN_SIGMA = 5.0


@dataclass(frozen=True)
class CostModel:
    """Costs of trading an instrument. Applied ONLY by engine.py.

    All as a fraction of the traded notional (e.g. 0.0001 = 1 bp), except
    ``commission_per_unit`` which is per unit of rotated weight.
    """

    spread: float = 0.0001          # effective half spread per side (per rotated unit)
    slippage: float = 0.00005       # slippage per side (per rotated unit)
    impact: float = 0.0             # market impact per rotated unit
    commission: float = 0.0         # commission per rotated unit
    # --- Swap, now DIRECTIONAL (two separated components, both DAILY on |weight|
    #     or weight held, not turnover) ---
    # carry: SIGNED daily rate differential a LONG position earns (+ = long
    #   receives income, − = long pays). A SHORT earns −carry. In a long/short
    #   book this partially cancels; it is NOT a cost, it is a P&L term.
    # swap_margin: the broker's markup, ALWAYS a cost on |weight|/day
    #   (unidirectional). This is what does not cancel in a balanced book.
    # Engine applies:  swap_cost = swap_margin·|w_prev| − carry·w_prev.
    # See SWAP_CALIBRATION below (real published sources, dated).
    carry: float = 0.0
    swap_margin: float = 0.00003    # ~0.30 bp/day (afterprime/FTMO published, 2026-08)


# =========================================================================== #
# SWAP CALIBRATION — real published sources, dated (como SHARPE_REFERENCE)     #
# =========================================================================== #
# El swap real se separa en (a) diferencial de tasas CON SIGNO y (b) margen del
# broker unidireccional.
#
# (a) CARRY — HISTÓRICO, no un snapshot. Series mensuales de tasas de política de
#     BIS (WS_CBPOL), 2003-2026, descargadas a data/rates/policy_rates.csv
#     (consultado 2026-08-22, stats.bis.org/api/v1). Se construye una MATRIZ
#     fecha×instrumento en src/rates.py (reindexada a diario, ffill). USAR UN
#     SNAPSHOT DE 2026 SOBRE 2005-2023 ESTABA MAL: las tasas reales fueron muy
#     distintas y el signo del carry se INVIERTE en parte de la muestra (p. ej.
#     EURUSD fue POSITIVO en 2009-2015, cuando EUR>USD). carry(long XXXYYY) =
#     (r_XXX − r_YYY); cruces aditivos; índices (div_yield − financing); metales
#     −financing. Los div_yield de índices se mantienen CONSTANTES (simplificación;
#     se mueven poco, efecto de 2º orden): SPX 1.3, GER40 2.5, JPN225 1.8, HK50 3.5.
#     El snapshot _POLICY_RATE de abajo es sólo para el carry "actual"
#     (CostModel.carry escalar, uso live); los BACKTESTS pasan la matriz histórica.
#
# (b) SWAP_MARGIN — tabla long/short publicada de un broker (afterprime.com/swaps,
#     2026-08-23): EURUSD −9.43/+1.31 → margen ≈0.35 bp/d; XAUUSD −70/+29.26 →
#     ≈0.47. Validado vs el ejemplo de FTMO (~0.43 bp/d EURUSD). Base ~0.30 bp/d
#     (metales ~0.45), escalable con BROKER_MARGIN_MULT.
#
# CONVENCIÓN 360→261 (bug corregido): el broker cobra 365 días de carry/margen
# repartidos en ~261 SESIONES (swap triple del miércoles). El motor aplica el
# cargo sólo en días de cotización, así que AMBOS componentes se multiplican por
# TRADING_DAY_SWAP_FACTOR = 365/261 ≈ 1.40. Consecuencia registrada: el margen
# efectivo sube a 0.30×1.40 = 0.42 bp/d — el modelo corregido es MÁS punitivo en
# margen que el placeholder unsigned (0.30) que mató a H001/H007, no menos.
#
# VALIDACIÓN CRUZADA (dos fuentes independientes, al 2026-08, dentro del 10%):
#   carry implícito del broker = (swap_long − swap_short)/2 [antes del factor]
#     EURUSD: broker −0.46 bp/d  vs  tasas −0.556 bp/d
#     XAUUSD: broker −1.15 bp/d  vs  tasas −1.25 bp/d
#
# LIMITACIÓN: los swaps son dinámicos; margen y div_yields son snapshots fechados.
TRADING_DAY_SWAP_FACTOR = 365.0 / 261.0   # 365 días de carry sobre ~261 sesiones

_POLICY_RATE = {  # % anual — SNAPSHOT actual (BIS 2026-07); sólo para el carry live
    "USD": 4.50, "EUR": 2.50, "GBP": 4.50, "JPY": 0.50,
    "AUD": 4.10, "CAD": 2.75, "CHF": 0.25, "HKD": 4.50,
}
_DIV_YIELD = {"SPX500": 1.3, "GER40": 2.5, "JPN225": 1.8, "HK50": 3.5}  # % anual, constante
_INDEX_CCY = {"SPX500": "USD", "GER40": "EUR", "JPN225": "JPY", "HK50": "HKD"}
_FX_LEGS = {  # (base, quote) para majors + cruces
    "EURUSD": ("EUR", "USD"), "GBPUSD": ("GBP", "USD"), "USDJPY": ("USD", "JPY"),
    "AUDUSD": ("AUD", "USD"), "USDCAD": ("USD", "CAD"),
    "EURJPY": ("EUR", "JPY"), "GBPJPY": ("GBP", "JPY"), "AUDJPY": ("AUD", "JPY"),
    "EURAUD": ("EUR", "AUD"), "GBPAUD": ("GBP", "AUD"), "EURCHF": ("EUR", "CHF"),
}
BROKER_MARGIN_MULT = 1.0            # 1.0 = afterprime/FTMO raw; prop firm peor → sensibilidad {1.0, 1.5}
_MARGIN_FX = 0.00003               # 0.30 bp/noche (antes del factor 365/261)
_MARGIN_METAL = 0.000045           # 0.45 bp/noche
_MARGIN_INDEX = 0.00003


def _carry_daily(sym: str) -> float:
    """Carry 'actual' (snapshot) por sesión — sólo uso live; los backtests usan
    la matriz histórica de src/rates.py. Incluye el factor 365/261."""
    f = TRADING_DAY_SWAP_FACTOR / 100.0 / 360.0
    if sym in _FX_LEGS:
        base, quote = _FX_LEGS[sym]
        return (_POLICY_RATE[base] - _POLICY_RATE[quote]) * f
    if sym in ("XAUUSD", "XAGUSD"):
        return -_POLICY_RATE["USD"] * f
    if sym in _DIV_YIELD:
        return (_DIV_YIELD[sym] - _POLICY_RATE[_INDEX_CCY[sym]]) * f
    return 0.0


def _margin_daily(sym: str) -> float:
    base = _MARGIN_METAL if sym in ("XAUUSD", "XAGUSD") else (
        _MARGIN_INDEX if sym in _DIV_YIELD else _MARGIN_FX)
    return base * BROKER_MARGIN_MULT * TRADING_DAY_SWAP_FACTOR   # 365/261 convención


def _cost_for(sym: str) -> CostModel:
    return CostModel(carry=_carry_daily(sym), swap_margin=_margin_daily(sym))


# Default cost model and per-instrument overrides (directional swap calibrated above).
DEFAULT_COST = CostModel()
COSTS: dict[str, CostModel] = {sym: _cost_for(sym) for sym in INSTRUMENTS}


@dataclass(frozen=True)
class SharpeReference:
    """Known historical reference Sharpe to verify the engine.

    The verification is expressed as a tolerance, not exact equality, and the
    source/window are fixed here so that the test is reproducible.
    """

    instrument: str
    value: float
    window: str          # e.g. "2005-2023"
    source: str          # where the reference number comes from
    tolerance: float     # absolute tolerance allowed on the Sharpe


# Default reference for the engine.py verification test.
# NOTE: the concrete value is fixed once the real historical data is available;
# the acceptance test reads this structure.
SHARPE_REFERENCE = SharpeReference(
    instrument="SPX500",
    value=0.80,
    window="2011-09-19 to 2026-08-14",
    source=(
        "WHAT IS ACTUALLY VERIFIED (name it precisely): the EXTERNAL check is that the "
        "series IS the S&P price index — its start level (1204.1 on 2011-09-19) matches "
        "the public record (Wikipedia 'Closing milestones of the S&P 500': index ~1200 "
        "mid-Sep 2011, <1100 by 2011-10-04; consulted 2026-08-18). IF the series is the "
        "index, its Sharpe IS the index's Sharpe BY CONSTRUCTION — this is NOT a "
        "comparison against a published figure/paper. The 0.80 (geometric: CAGR 13.3% / "
        "vol 16.9%) vs 0.82 (engine.sharpe, arithmetic mean) agreement is an INTERNAL "
        "cross-check between two estimators on the same series, not external. "
        "Price-return (the CFD pays no dividends), not total-return. PENDING to fully "
        "close: (a) verify the END endpoint (2026-08-14 = 7780.0) against the public "
        "S&P close, and (b) record a precise independent daily close (Stooq/Yahoo ^SPX) "
        "with its consult date — neither could be fetched in-session (Stooq CSV empty; "
        "FRED keeps only 10y of daily)."
    ),
    tolerance=0.10,
)

# Trading days per year (fallback for synthetic series without a calendar; real
# series are annualized with their own observed bars/year — see engine.bars_per_year).
TRADING_DAYS_PER_YEAR = 252

# Max gross exposure `sum(|weights|)` allowed for a conforming signal. Relaxed
# from a hard 1: TSMOM with inverse-vol sizing over several instruments runs 2-4×
# gross naturally; forcing ≤1 would crush volatility below target and break the
# comparison against the literature. Absolute risk is controlled downstream by
# vol-targeting and the simulator's leverage scaling, not by this cap.
MAX_GROSS_EXPOSURE = 4.0

# Sacred holdout (master document §3.5): the last 3 years are reserved and never
# touched until a hypothesis's final validation. The policy — and H001's explicit
# EXEMPTION (it is a pure external-replication calibration test, no tuning on our
# data) — is documented in hypotheses/HOLDOUT.md. The holdout starts governing from
# the first discovery/optimization hypothesis (H002 onward unless also exempt).
from datetime import date as _date  # noqa: E402

HOLDOUT_START = _date(2023, 8, 17)  # inclusive; last ~3 years reserved


# --- Prop-firm rules (parameterized; do NOT hardcode a single firm) ---
@dataclass(frozen=True)
class FirmRules:
    """Rules of a funded-account challenge.

    All barrier magnitudes are expressed as a FRACTION of the initial capital
    (e.g. 0.10 = 10%). The drawdown is STATIC (against initial capital, not
    trailing — master document section 2.2).

    NOTE on additive P&L: the simulator accumulates P&L ADDITIVELY over the
    initial capital (static sizing), faithful to the real challenge contract
    (target and drawdown in monetary units against the initial balance, not in
    log-space). Log-space would ONLY matter again with compound sizing over a
    funded account with a trailing rule; it is not corrected now.
    """

    phase1_target: float = 0.10        # phase 1 target (+10%)
    phase2_target: float = 0.05        # phase 2 target (+5%)
    daily_loss_limit: float = 0.05     # daily loss limit (5%)
    max_drawdown: float = 0.10         # static max drawdown (10%)
    n_payouts: int = 4                 # number of payout cycles N considered
    fee: float = 500.0                 # challenge fee cost (USD)
    # Length of a payout cycle (~1 month). Used by the funded-phase survival
    # simulation that produces P(burn). (The provisional per-year value that used
    # profit_split/account_capital was retired — it was misspecified and carried a
    # hidden knob; the real threshold objective is built in weeks 9-10.)
    payout_interval_days: int = 21


DEFAULT_FIRM_RULES = FirmRules()


# --- Barrier simulator parameters (challenge.py) ---
@dataclass(frozen=True)
class SimulatorParams:
    """Configuration of the block-bootstrap barrier simulator."""

    block_size: int = 20               # block size (>1; ~1 month of trading)
    n_bootstraps: int = 10_000         # number of simulated paths
    horizon_days: int = 756            # max horizon per phase (~3 years; FTMO
                                       # removed the time limit, so the horizon
                                       # is a modeling choice, not a firm rule)
    seed: int = 12345                  # seed for reproducibility
    # If the UNRESOLVED fraction of any phase exceeds this threshold, the economic
    # value is not reported (insufficient horizon) instead of a misleading number.
    unresolved_threshold: float = 0.05
    # Leverage grid: multipliers k evaluated for the P(pass) curve.
    leverage_min: float = 0.25
    leverage_max: float = 3.0
    leverage_step: float = 0.25


DEFAULT_SIM_PARAMS = SimulatorParams()
