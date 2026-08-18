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
    expected_net_value: float
    # Three-outcome accounting for phase 1 (sum to 1 with p_phase1).
    p_fail: float = 0.0
    p_unresolved: float = 0.0
    horizon_days: int = 0
    leverage_grid: np.ndarray = field(default_factory=lambda: np.array([]))
    leverage_pass_curve: np.ndarray = field(default_factory=lambda: np.array([]))
    leverage_value_curve: np.ndarray = field(default_factory=lambda: np.array([]))
    optimal_leverage: float = 1.0


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
    The first event wins (first passage). `day_index` = day of the passing event
    (or the horizon if it does not pass).
    """
    n_paths, horizon = paths.shape
    level = np.zeros(n_paths)          # accumulated (additive) P&L vs initial capital
    passed = np.zeros(n_paths, dtype=bool)
    burned = np.zeros(n_paths, dtype=bool)
    day_passed = np.full(n_paths, horizon, dtype=int)

    for t in range(horizon):
        active = ~passed & ~burned
        if not active.any():
            break
        r_t = paths[:, t]
        level = np.where(active, level + r_t, level)
        pnl = level

        # Burn: violation of the daily limit or the static drawdown.
        burn_now = active & ((r_t <= -daily_loss_limit) | (pnl <= -max_drawdown))
        burned |= burn_now

        # Pass: reaches the target without having burned on this same day.
        pass_now = active & ~burn_now & (pnl >= target)
        newly = pass_now & ~passed
        day_passed = np.where(newly, t + 1, day_passed)
        passed |= pass_now

    # Three-outcome accounting: whoever neither passed nor burned is UNRESOLVED.
    outcome = np.full(n_paths, UNRESOLVED, dtype=np.int8)
    outcome[passed] = PASSED
    outcome[burned] = FAILED
    return outcome, day_passed


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
    passed1 = outcome1 == PASSED
    p_phase1 = float(passed1.mean())
    p_fail1 = float((outcome1 == FAILED).mean())
    p_unresolved1 = float((outcome1 == UNRESOLVED).mean())

    # --- Phase 2 (independent; P(both) = P1 * P2 conditional approx.) ---
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
    passed2 = outcome2 == PASSED
    p_phase2 = float(passed2.mean())
    p_both = p_phase1 * p_phase2

    # Expected days to pass both phases (conditional on passing). If nothing
    # passes within the horizon in some phase, it is capped at the total horizon.
    if passed1.any() and passed2.any():
        expected_days = float(days1[passed1].mean() + days2[passed2].mean())
    else:
        expected_days = float(params.horizon_days * 2)

    # --- P(burn the funded account before payout N) ---
    # After funding, each payout cycle is like surviving without violating
    # DD/daily. Reuse phase 2 as a proxy for a "payout cycle": burn = not survive.
    p_survive_cycle = p_phase2
    p_burn_before_payout = float(1.0 - p_survive_cycle**rules.n_payouts)

    # --- Expected net value after fees (puts a price on time) ---
    expected_net = _expected_net_value(
        p_both, p_burn_before_payout, expected_days, rules
    )

    result = ChallengeResult(
        p_phase1=p_phase1,
        p_phase2=p_phase2,
        p_both=p_both,
        expected_days_to_pass=expected_days,
        p_burn_before_payout=p_burn_before_payout,
        expected_net_value=expected_net,
        p_fail=p_fail1,
        p_unresolved=p_unresolved1,
        horizon_days=int(params.horizon_days),
    )

    # --- Leverage curve ---
    # The P(pass) curve is reported as a DIAGNOSTIC (monotonically decreasing in
    # leverage with an honest horizon), but the DECISION leverage comes from
    # maximizing the expected net value, which prices the time/tied-up capital
    # of low leverage. argmax(P) would give the minimum leverage.
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
        result.leverage_pass_curve = np.array([s.p_both for s in sub])
        result.leverage_value_curve = np.array([s.expected_net_value for s in sub])
        result.optimal_leverage = float(grid[int(np.argmax(result.leverage_value_curve))])

    return result


def _expected_net_value(
    p_both: float,
    p_burn_before_payout: float,
    expected_days: float,
    rules: config.FirmRules,
) -> float:
    """Expected net value after fees — puts a price on time.

    - Expected number of attempts until passing both phases ~ geometric:
      1/P(both).
    - Fee cost = attempts · fee.
    - Time cost = expected days (per attempt) · attempts · daily cost of tied-up
      capital. This term is what makes the leverage optimum INTERIOR: without
      it, lowering the leverage would only raise P and the optimum would fall at
      the minimum (waiting almost forever).
    - Income after funding = expected payout weighted by surviving the payout.

    Explicit economic assumption: `rules.daily_capital_cost` is the daily
    opportunity cost of the capital while attempting the challenge.
    """
    if p_both <= 0:
        # Never passes within the horizon: only fees and time accumulate.
        return -1e12
    expected_attempts = 1.0 / p_both
    expected_fee_cost = expected_attempts * rules.fee
    expected_time_cost = expected_attempts * expected_days * rules.daily_capital_cost
    expected_income = (1.0 - p_burn_before_payout) * rules.payout_per_cycle * rules.n_payouts
    return float(expected_income - expected_fee_cost - expected_time_cost)


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
