"""challenge.py — Barrier simulator (THE differentiating CORE).

A funded-account challenge is a first-passage problem with a double barrier:
P(hit +target before −limit), not a trading problem. This module estimates that
probability and the expected economic value by simulation.

Method: block bootstrap (moving-block, NOT i.i.d.) of the net daily returns
produced by engine.py. It preserves autocorrelation and volatility clustering;
an i.i.d. resample would underestimate the realistic volatility and give an
optimistic, false P(pass) (master document section 2.1).

Outputs (section 3.4):
- P(pass phase 1), P(pass phase 2), P(pass both)
- Expected days to pass
- P(burn the funded account before payout N)
- Expected net value after fees  ← the deciding metric
- P(pass) vs leverage curve → optimal multiplier

Verification: against the closed-form analytic first-passage formula with a
double barrier (see `analytic_pass_probability`), not against intuition.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from src import config


# --------------------------------------------------------------------------- #
# Result                                                                       #
# --------------------------------------------------------------------------- #
# Possible outcomes of a path (three-outcome accounting).
UNRESOLVED = 0  # reached the horizon without touching any barrier
PASSED = 1      # reached the target
FAILED = 2      # hit the daily limit or the max drawdown


@dataclass
class ChallengeResult:
    """Outputs of the barrier simulator."""

    p_phase1: float
    p_phase2: float
    p_both: float
    expected_days_to_pass: float
    p_burn_before_payout: float
    # Economic value per YEAR (fraction/USD), or nan when the horizon is
    # insufficient (see `insufficient_horizon`). This is the deciding metric.
    expected_net_value: float
    # Decision probability, CONDITIONAL ON ABSORPTION: p_cond = pass/(pass+fail).
    # This is the correct first-passage probability; UNRESOLVED is not a failure.
    p_pass_conditional: float = 0.0
    # Three-outcome accounting for phase 1 (sum to 1 with p_phase1).
    p_fail: float = 0.0
    p_unresolved: float = 0.0
    # True when the UNRESOLVED fraction exceeds the threshold in any phase; the
    # economic value is then nan (a number there would be misleading).
    insufficient_horizon: bool = False
    horizon_days: int = 0
    leverage_grid: np.ndarray = field(default_factory=lambda: np.array([]))
    # Two diagnostic curves, always reported. NEITHER is collapsed into a single
    # optimum yet — see `optimal_leverage`.
    leverage_pass_curve: np.ndarray = field(default_factory=lambda: np.array([]))
    leverage_value_curve: np.ndarray = field(default_factory=lambda: np.array([]))
    # DECISION (week 6): optimal_leverage is UNDEFINED (None) until the funded
    # phase is modeled (weeks 9-10) and the objective — expected value per unit
    # time with an ENDOGENOUS payout — is built. Picking an optimum now would be
    # determined by a modeling knob (horizon_days / leverage_min / a cost term),
    # not by the data. An honest None beats a number that points the wrong way.
    optimal_leverage: float | None = None
    optimal_leverage_reason: str = ""


# --------------------------------------------------------------------------- #
# Block bootstrap                                                             #
# --------------------------------------------------------------------------- #
def block_bootstrap(
    returns: np.ndarray,
    *,
    n_paths: int,
    horizon: int,
    block_size: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Generate a (n_paths, horizon) matrix by moving-block bootstrap.

    Contiguous blocks of length `block_size` are picked from random start
    positions (with wrap-around) and concatenated until `horizon` is covered.
    `block_size=1` is equivalent to i.i.d. (only for analytic verification).
    """
    r = np.asarray(returns, dtype=float)
    n = r.size
    if n == 0:
        raise ValueError("returns vacío")
    if block_size < 1:
        raise ValueError("block_size debe ser >= 1")

    n_blocks = int(np.ceil(horizon / block_size))
    # Start positions of each block, for all paths.
    starts = rng.integers(0, n, size=(n_paths, n_blocks))
    # Offsets within the block: 0..block_size-1
    offsets = np.arange(block_size)
    # Indices (n_paths, n_blocks, block_size) with wrap-around.
    idx = (starts[:, :, None] + offsets[None, None, :]) % n
    sampled = r[idx].reshape(n_paths, n_blocks * block_size)
    return sampled[:, :horizon]


# --------------------------------------------------------------------------- #
# Barrier evaluation (first passage)                                          #
# --------------------------------------------------------------------------- #
def _first_passage(
    paths: np.ndarray, target: float, daily_loss_limit: float, max_drawdown: float
) -> tuple[np.ndarray, np.ndarray]:
    """Evaluate each path and return (outcome, day_index).

    `outcome` is a vector with the THREE-OUTCOME ACCOUNTING:
    `PASSED` (hit the target), `FAILED` (hit the daily limit or the static max
    drawdown), or `UNRESOLVED` (reached the end of the horizon without touching
    any barrier). UNRESOLVED is NEVER folded into FAILED: folding it would
    invert the system's conclusion (low volatility takes longer to absorb and
    would be punished as a failure).

    P&L is accumulated ADDITIVELY over the initial capital (static sizing
    relative to the initial balance), which is what defines a challenge: target
    and drawdown are measured as a fraction of the INITIAL capital, not
    compounded. This also matches the analytic first-passage formula (additive
    process).

    Rules, evaluated per day:
    - PASS: pnl >= target
    - BURN: daily return <= -daily_loss_limit  (daily loss limit)
            or pnl <= -max_drawdown            (static drawdown vs initial)
    The first event wins (first passage). `day_absorbed` = the day the barrier was
    touched, recorded for BOTH passing AND burning trajectories (or the horizon if
    the path never absorbs). Recording the burn day too is required so the economic
    layer can price the time consumed by FAILED attempts, not only the winners.
    """
    n_paths, horizon = paths.shape
    level = np.zeros(n_paths)          # accumulated (additive) P&L vs initial capital
    passed = np.zeros(n_paths, dtype=bool)
    burned = np.zeros(n_paths, dtype=bool)
    day_absorbed = np.full(n_paths, horizon, dtype=int)

    for t in range(horizon):
        active = ~passed & ~burned
        if not active.any():
            break
        r_t = paths[:, t]
        level = np.where(active, level + r_t, level)
        pnl = level

        # Burn: violation of the daily limit or the static drawdown.
        burn_now = active & ((r_t <= -daily_loss_limit) | (pnl <= -max_drawdown))
        # Pass: reaches the target without having burned on this same day.
        pass_now = active & ~burn_now & (pnl >= target)

        # burn_now/pass_now are gated on `active`, so they are inherently "newly".
        day_absorbed = np.where(burn_now | pass_now, t + 1, day_absorbed)
        burned |= burn_now
        passed |= pass_now

    # Three-outcome accounting: whoever neither passed nor burned is UNRESOLVED.
    outcome = np.full(n_paths, UNRESOLVED, dtype=np.int8)
    outcome[passed] = PASSED
    outcome[burned] = FAILED
    return outcome, day_absorbed


# --------------------------------------------------------------------------- #
# Main simulator                                                              #
# --------------------------------------------------------------------------- #
def simulate_challenge(
    returns,
    *,
    rules: config.FirmRules = config.DEFAULT_FIRM_RULES,
    params: config.SimulatorParams = config.DEFAULT_SIM_PARAMS,
    leverage: float = 1.0,
    with_leverage_curve: bool = True,
) -> ChallengeResult:
    """Estimate P(pass) and the economic metrics of a challenge.

    `returns`: series/array of net daily returns (from engine.py).
    `leverage`: multiplier applied to the returns for this run.
    """
    r = np.asarray(getattr(returns, "to_numpy", lambda: returns)(), dtype=float)
    r = r[np.isfinite(r)]
    if r.size == 0:
        raise ValueError("returns sin datos finitos")

    rng = np.random.default_rng(params.seed)
    scaled = r * leverage

    # --- Phase 1 ---
    paths1 = block_bootstrap(
        scaled,
        n_paths=params.n_bootstraps,
        horizon=params.horizon_days,
        block_size=params.block_size,
        rng=rng,
    )
    outcome1, days1 = _first_passage(
        paths1, rules.phase1_target, rules.daily_loss_limit, rules.max_drawdown
    )
    s1 = _PhaseStats.of(outcome1, days1)

    # --- Phase 2 ---
    paths2 = block_bootstrap(
        scaled,
        n_paths=params.n_bootstraps,
        horizon=params.horizon_days,
        block_size=params.block_size,
        rng=rng,
    )
    outcome2, days2 = _first_passage(
        paths2, rules.phase2_target, rules.daily_loss_limit, rules.max_drawdown
    )
    s2 = _PhaseStats.of(outcome2, days2)

    p_both = s1.p_pass * s2.p_pass  # raw (diagnostic only; NOT used for decisions)

    # --- Decision probability CONDITIONAL ON ABSORPTION ---
    # An attempt does not end at the horizon; it ends when it hits a barrier.
    # UNRESOLVED is a horizon-quality signal, not a failure.
    p_cond = s1.p_cond * s2.p_cond

    # --- Guard: insufficient horizon ---
    insufficient = (
        s1.p_unresolved > params.unresolved_threshold
        or s2.p_unresolved > params.unresolved_threshold
    )

    # --- Funded phase (derives payout & burn; both scale with leverage) ---
    p_survive_cycle, payout_frac = _funded_phase(scaled, rules, params, rng)
    p_burn_before_payout = float(1.0 - p_survive_cycle**rules.n_payouts)

    # --- Expected days to pass, INCLUDING failed attempts (both absorb) ---
    if p_cond > 0:
        expected_attempts = 1.0 / p_cond
        per_attempt_days = s1.mean_absorb_day + s1.p_cond * s2.mean_absorb_day
        expected_days = float(expected_attempts * per_attempt_days)
    else:
        expected_attempts = float("inf")
        expected_days = float("nan")

    # --- Economic value per year (nan when horizon insufficient) ---
    expected_net = _economic_value(
        p_cond, p_survive_cycle, payout_frac, expected_days, insufficient, rules
    )

    result = ChallengeResult(
        p_phase1=s1.p_pass,
        p_phase2=s2.p_pass,
        p_both=p_both,
        expected_days_to_pass=expected_days,
        p_burn_before_payout=p_burn_before_payout,
        expected_net_value=expected_net,
        p_pass_conditional=p_cond,
        p_fail=s1.p_fail,
        p_unresolved=s1.p_unresolved,
        insufficient_horizon=insufficient,
        horizon_days=int(params.horizon_days),
    )

    # --- Leverage curves (both reported; NO single optimum yet) ---
    # Two diagnostics: the conditional-P(pass) curve (favors low leverage — the
    # §2.1 thesis) and the provisional value-per-year curve (endogenous payout).
    # We do NOT pick optimal_leverage from either: over P alone the optimum is a
    # degenerate minimum, and the value objective is not final until the funded
    # phase is modeled (weeks 9-10). Collapsing to a number now would be driven
    # by a modeling knob, not the data. See the DECISION note on ChallengeResult.
    if with_leverage_curve:
        grid = np.arange(
            params.leverage_min,
            params.leverage_max + params.leverage_step / 2,
            params.leverage_step,
        )
        sub = [
            simulate_challenge(
                r, rules=rules, params=params, leverage=float(k),
                with_leverage_curve=False,
            )
            for k in grid
        ]
        result.leverage_grid = grid
        result.leverage_pass_curve = np.array([s.p_pass_conditional for s in sub])
        result.leverage_value_curve = np.array([s.expected_net_value for s in sub])
        result.optimal_leverage = None
        result.optimal_leverage_reason = (
            "objetivo no definido; ver spec challenge-simulator §leverage "
            "(pendiente del modelo de fase fondeada, sem 9-10)"
        )

    return result


@dataclass
class _PhaseStats:
    """Per-phase outcome statistics, conditional on absorption."""

    p_pass: float
    p_fail: float
    p_unresolved: float
    p_cond: float          # pass / (pass + fail) — conditional on absorption
    mean_absorb_day: float  # mean day of absorption over PASSED and FAILED paths

    @classmethod
    def of(cls, outcome: np.ndarray, day_absorbed: np.ndarray) -> "_PhaseStats":
        passed = outcome == PASSED
        failed = outcome == FAILED
        absorbed = passed | failed
        p_pass = float(passed.mean())
        p_fail = float(failed.mean())
        p_unres = float((outcome == UNRESOLVED).mean())
        denom = p_pass + p_fail
        p_cond = float(p_pass / denom) if denom > 0 else 0.0
        mean_day = float(day_absorbed[absorbed].mean()) if absorbed.any() else float("nan")
        return cls(p_pass, p_fail, p_unres, p_cond, mean_day)


def _funded_phase(
    scaled: np.ndarray,
    rules: config.FirmRules,
    params: config.SimulatorParams,
    rng: np.random.Generator,
) -> tuple[float, float]:
    """Simulate one funded-phase payout cycle to DERIVE payout and survival.

    Over a payout window, the funded account has only the loss barriers (daily
    limit and static drawdown), no target. Returns:
    - `p_survive`: fraction of windows that survive without hitting a loss barrier.
      Falls as leverage rises → P(burn) rises with leverage (correct).
    - `payout_frac`: profit_split × E[end P&L fraction | survived, clipped ≥ 0].
      Rises with leverage/volatility → the payout SCALES with the return, so the
      interior optimum emerges from a real trade-off, not an invented cost knob.
    """
    paths = block_bootstrap(
        scaled,
        n_paths=params.n_bootstraps,
        horizon=rules.payout_interval_days,
        block_size=params.block_size,
        rng=rng,
    )
    level = np.cumsum(paths, axis=1)
    daily_hit = (paths <= -rules.daily_loss_limit).any(axis=1)
    dd_hit = (level <= -rules.max_drawdown).any(axis=1)
    survived = ~(daily_hit | dd_hit)
    p_survive = float(survived.mean())
    if survived.any():
        profit = max(0.0, float(level[survived, -1].mean()))
    else:
        profit = 0.0
    payout_frac = rules.profit_split * profit
    return p_survive, payout_frac


def _economic_value(
    p_cond: float,
    p_survive_cycle: float,
    payout_frac: float,
    expected_days: float,
    insufficient_horizon: bool,
    rules: config.FirmRules,
) -> float:
    """Economic value per YEAR, conditional on absorption.

    Returns nan (never a magic sentinel) when the value is undefined: the horizon
    is insufficient, nobody passes, or there is no elapsed time. nan is excluded
    from the leverage argmax rather than dominating it.

    - Expected attempts to pass both phases = 1 / p_cond (conditional pass).
    - Fee cost = attempts · fee.
    - Funded income = payout (derived, scales with return) × expected number of
      collected payouts before burning.
    - Total time = challenge time (incl. failed attempts) + funded time.
    """
    if insufficient_horizon or p_cond <= 0 or not np.isfinite(expected_days):
        return float("nan")

    expected_attempts = 1.0 / p_cond
    fee_cost = expected_attempts * rules.fee

    # Renewal model: after funding you collect a payout each surviving cycle and
    # keep going until you BURN, then you must re-qualify (pay the challenge fee
    # again). Expected payouts collected before the first burn is geometric and
    # UNCAPPED: s/(1-s). Surviving (low leverage) is rewarded with many cycles;
    # burning fast (high leverage) cuts them off. This is what makes the optimum
    # interior — the real trade-off, not an invented cost.
    s = min(p_survive_cycle, 0.9995)  # cap to keep the limit finite
    expected_payouts = s / (1.0 - s)
    payout_usd = payout_frac * rules.account_capital
    income = payout_usd * expected_payouts

    funded_days = expected_payouts * rules.payout_interval_days
    total_days = expected_days + funded_days
    if total_days <= 0:
        return float("nan")
    years = total_days / config.TRADING_DAYS_PER_YEAR
    return float((income - fee_cost) / years)


# --------------------------------------------------------------------------- #
# Analytic oracle (verification, not engine)                                  #
# --------------------------------------------------------------------------- #
def analytic_pass_probability(mu: float, sigma: float, a: float, b: float) -> float:
    """Closed-form first-passage formula with a double barrier.

    P(hit +b before −a) for a drift `mu` and volatility `sigma`:
        P = [1 − e^(−2μa/σ²)] / [1 − e^(−2μ(a+b)/σ²)]
    With μ=0 the limit is a/(a+b) (0.5 if a=b).
    """
    if sigma <= 0:
        raise ValueError("sigma debe ser > 0")
    if mu == 0:
        return a / (a + b)
    k = 2.0 * mu / (sigma**2)
    return float((1.0 - np.exp(-k * a)) / (1.0 - np.exp(-k * (a + b))))
