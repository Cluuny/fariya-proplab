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
RESULTS = ROOT / "results"

# --- Universe (master document, section 8.2) ---
# Corrected from the original: NAS100 and UK100 were dropped (four equity indices,
# three highly correlated, no energy, no Asia — the worst mix for a portfolio whose
# whole point is to lower volatility by decorrelation). Replaced by JPN225 (Nikkei,
# Asia) and BRENT (energy) for cross-class / cross-geography diversification.
INSTRUMENTS: tuple[str, ...] = (
    "EURUSD",
    "GBPUSD",
    "USDJPY",
    "AUDUSD",
    "USDCAD",
    "XAUUSD",
    "SPX500",
    "GER40",
    "JPN225",
    "BRENT",
)

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
    "XAUUSD": "XAUUSD",
    "SPX500": "USA500IDXUSD",
    "GER40": "DEUIDXEUR",
    "JPN225": "JPNIDXJPY",
    "BRENT": "BRENTCMDUSD",
}

# Price scale factor per instrument for the .bi5 integer prices (verified for
# EURUSD = 1e5; the rest are the community-known point values). COSMETIC: returns
# (pct_change) and Sharpe are scale-invariant, so a wrong factor changes only the
# displayed price level, not any downstream metric.
DUKASCOPY_POINT: dict[str, float] = {
    "EURUSD": 1e5, "GBPUSD": 1e5, "AUDUSD": 1e5, "USDCAD": 1e5,
    "USDJPY": 1e3, "XAUUSD": 1e3,
    "SPX500": 1e3, "GER40": 1e3, "JPN225": 1e3, "BRENT": 1e3,
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

    spread: float = 0.0001          # effective half spread per side
    slippage: float = 0.00005       # slippage per side
    impact: float = 0.0             # market impact per rotated unit
    commission: float = 0.0         # commission per rotated unit


# Default cost model and per-instrument overrides.
DEFAULT_COST = CostModel()
COSTS: dict[str, CostModel] = {sym: DEFAULT_COST for sym in INSTRUMENTS}


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
    value=0.77,
    window="2011-2026",
    source=(
        "Dukascopy SPX500 CFD daily buy&hold (via dukascopy-node). Data-derived "
        "regression anchor, consistent with the known strong S&P 500 Sharpe (~0.7-0.8) "
        "over the 2011-2026 bull market. NOT a fully independent external check — a "
        "published total-return Sharpe for the exact period would green milestone 2."
    ),
    tolerance=0.15,
)

# Trading days per year, to annualize Sharpe.
TRADING_DAYS_PER_YEAR = 252


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
