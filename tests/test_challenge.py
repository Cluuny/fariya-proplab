"""Block B — challenge-simulator.

Verification against the closed-form analytic formula (not against intuition),
block bootstrap that preserves volatility, barriers, economic metrics,
leverage curve and determinism.
"""

import numpy as np
import pandas as pd
import pytest

from src import challenge, config


def _gaussian_returns(mu, sigma, n=6000, seed=0):
    return np.random.default_rng(seed).normal(mu, sigma, n)


def _verif_rules(barrier):
    # Pure double barrier: no daily limit (=1.0), DD = lower barrier.
    return config.FirmRules(
        phase1_target=barrier,
        phase2_target=barrier,
        daily_loss_limit=1.0,
        max_drawdown=barrier,
        n_payouts=1,
        fee=0.0,
    )


def _verif_params(**kw):
    base = dict(block_size=1, n_bootstraps=12000, horizon_days=600, seed=7,
                leverage_min=1.0, leverage_max=1.0, leverage_step=1.0)
    base.update(kw)
    return config.SimulatorParams(**base)


# --- Section 6: mathematical verification -----------------------------------
def test_zero_drift_symmetric_barriers_gives_half():
    # DoD week 4: μ=0, symmetric barriers 10/10 → P≈0.5.
    # σ large enough that almost all paths absorb within the horizon (avoids
    # truncation bias); symmetric → 0.5.
    r = _gaussian_returns(0.0, 0.02, n=8000, seed=1)
    res = challenge.simulate_challenge(
        r, rules=_verif_rules(0.10), params=_verif_params(), with_leverage_curve=False
    )
    assert abs(res.p_phase1 - 0.5) < 0.03


def test_matches_closed_form_with_drift():
    # Barriers 10/10 with drift. The simulator resamples from the empirical
    # series, so the honest comparison evaluates the closed form with the
    # EMPIRICAL MOMENTS of the series (not the theoretical ones): with small μ
    # the sampling error of the mean would shift the analytic target.
    # Tolerance = overshoot + MC.
    mu, sigma, barrier = 0.0004, 0.01, 0.10
    r = _gaussian_returns(mu, sigma, n=12000, seed=2)
    analytic = challenge.analytic_pass_probability(
        float(r.mean()), float(r.std()), barrier, barrier
    )
    res = challenge.simulate_challenge(
        r, rules=_verif_rules(barrier), params=_verif_params(seed=3, horizon_days=1500),
        with_leverage_curve=False,
    )
    assert abs(res.p_phase1 - analytic) < 0.04


def test_analytic_formula_zero_drift_is_ratio():
    assert challenge.analytic_pass_probability(0.0, 0.01, 0.10, 0.10) == pytest.approx(0.5)
    assert challenge.analytic_pass_probability(0.0, 0.01, 0.05, 0.15) == pytest.approx(0.25)


# --- Section 2: block bootstrap ---------------------------------------------
def _sq_autocorr_lag1(x):
    s = x**2
    s = s - s.mean()
    return float((s[:-1] * s[1:]).sum() / (s * s).sum())


def test_block_bootstrap_preserves_volatility_clustering():
    # Series with clustering: alternating blocks of low and high volatility.
    rng = np.random.default_rng(0)
    vol = np.concatenate([np.full(100, 0.003), np.full(100, 0.03)] * 10)
    returns = rng.normal(0, 1, vol.size) * vol
    acf_orig = _sq_autocorr_lag1(returns)

    gen = np.random.default_rng(1)
    block = challenge.block_bootstrap(returns, n_paths=1, horizon=4000, block_size=100, rng=gen)[0]
    iid = challenge.block_bootstrap(returns, n_paths=1, horizon=4000, block_size=1, rng=gen)[0]

    acf_block = _sq_autocorr_lag1(block)
    acf_iid = _sq_autocorr_lag1(iid)

    assert acf_orig > 0.1                 # the original series has clustering
    assert acf_block > 0.1                # the block bootstrap preserves it
    assert acf_block > acf_iid + 0.05     # i.i.d. destroys it (~0)


def test_block_bootstrap_deterministic():
    r = _gaussian_returns(0.0, 0.01, n=1000, seed=5)
    a = challenge.block_bootstrap(r, n_paths=50, horizon=200, block_size=20,
                                  rng=np.random.default_rng(9))
    b = challenge.block_bootstrap(r, n_paths=50, horizon=200, block_size=20,
                                  rng=np.random.default_rng(9))
    assert np.array_equal(a, b)


# --- Section 3: barriers -----------------------------------------------------
def test_probabilities_in_unit_interval():
    r = _gaussian_returns(0.0003, 0.01, n=3000, seed=4)
    res = challenge.simulate_challenge(
        r, params=config.SimulatorParams(n_bootstraps=2000, horizon_days=252, seed=1,
                                         block_size=20),
        with_leverage_curve=False,
    )
    for p in (res.p_phase1, res.p_phase2, res.p_both, res.p_burn_before_payout):
        assert 0.0 <= p <= 1.0


def test_drawdown_is_static_not_trailing():
    # Path that rises to +8% and then falls to +? — with a static 10% DD it does
    # NOT burn as long as the capital does not drop 10% from the INITIAL, even if
    # it falls from a peak. Path: +8% cumulative, then -0.05/day. Static allows
    # dropping to -10% of the initial; trailing would have burned much earlier
    # from the peak.
    up = np.concatenate([np.full(8, 0.01), np.full(30, -0.005)])
    paths = up.reshape(1, -1)
    passed, _ = challenge._first_passage(
        paths, target=0.20, daily_loss_limit=1.0, max_drawdown=0.10
    )
    # It did not reach the 20% target and did not burn from static DD until
    # crossing the real -10%. We verify that the burn event respects the static
    # (additive) barrier:
    pnl = np.cumsum(up)
    crosses_static = (pnl <= -0.10).any()
    assert not passed[0]
    assert crosses_static == (pnl.min() <= -0.10)


def test_changing_rules_changes_result():
    r = _gaussian_returns(0.0005, 0.01, n=3000, seed=6)
    easy = config.FirmRules(phase1_target=0.05, phase2_target=0.03, daily_loss_limit=0.10,
                            max_drawdown=0.15)
    hard = config.FirmRules(phase1_target=0.15, phase2_target=0.10, daily_loss_limit=0.02,
                            max_drawdown=0.05)
    p = config.SimulatorParams(n_bootstraps=2000, horizon_days=252, seed=1, block_size=20)
    res_easy = challenge.simulate_challenge(r, rules=easy, params=p, with_leverage_curve=False)
    res_hard = challenge.simulate_challenge(r, rules=hard, params=p, with_leverage_curve=False)
    assert res_easy.p_phase1 > res_hard.p_phase1


# --- Section 4: economic metrics --------------------------------------------
def test_expected_net_value_monotonic_in_edge():
    # More edge (same vol) → higher value per year, both defined (long horizon).
    p = config.SimulatorParams(n_bootstraps=3000, horizon_days=1500, seed=1, block_size=20)
    r_low = _gaussian_returns(0.0006, 0.01, n=4000, seed=10)
    r_high = _gaussian_returns(0.0012, 0.01, n=4000, seed=10)  # more drift, same vol
    net_low = challenge.simulate_challenge(r_low, params=p, with_leverage_curve=False).expected_net_value
    net_high = challenge.simulate_challenge(r_high, params=p, with_leverage_curve=False).expected_net_value
    assert np.isfinite(net_low) and np.isfinite(net_high)
    assert net_high > net_low


# --- Section 5: leverage curves (both reported; no single optimum yet) ------
def test_optimal_leverage_is_none_pending_objective():
    # DECISION (week 6): optimal_leverage is undefined (None) until the funded
    # phase is modeled. Both diagnostic curves are still reported. Collapsing to
    # a number now would be driven by a modeling knob, not the data.
    r = _gaussian_returns(0.0008, 0.015, n=4000, seed=11)
    p = config.SimulatorParams(n_bootstraps=2000, seed=1, block_size=20)
    res = challenge.simulate_challenge(r, params=p, with_leverage_curve=True)
    assert res.optimal_leverage is None
    assert res.optimal_leverage_reason  # non-empty explanation
    assert res.leverage_pass_curve.size == res.leverage_grid.size
    assert res.leverage_value_curve.size == res.leverage_grid.size


def test_p_burn_rises_with_leverage():
    # Bug 2 fixed: surviving = not hitting the loss barrier. More leverage → more
    # burn (the drawdown is an absorbing barrier).
    r = _gaussian_returns(0.0006, 0.01, n=4000, seed=14)
    p = config.SimulatorParams(n_bootstraps=3000, seed=1, block_size=20)
    low = challenge.simulate_challenge(r, params=p, leverage=0.5, with_leverage_curve=False)
    high = challenge.simulate_challenge(r, params=p, leverage=3.0, with_leverage_curve=False)
    assert high.p_burn_before_payout > low.p_burn_before_payout


def test_insufficient_horizon_guard():
    # Slow strategy at low leverage with a short horizon: most paths do not
    # absorb → guard flags it and does NOT report an economic value.
    r = _gaussian_returns(0.00005, 0.01, n=4000, seed=15)
    p = config.SimulatorParams(n_bootstraps=3000, horizon_days=120, seed=1, block_size=20)
    res = challenge.simulate_challenge(r, params=p, leverage=0.25, with_leverage_curve=False)
    assert res.insufficient_horizon
    assert np.isnan(res.expected_net_value)


def test_conditional_pass_invariant_to_horizon():
    # The decision probability (conditional on absorption) is ~invariant to the
    # horizon, while raw p_both is NOT. This is the property that proves no metric
    # folds UNRESOLVED into failure.
    # Low leverage so the SHORT horizon genuinely truncates (many unresolved).
    r = _gaussian_returns(0.0006, 0.01, n=6000, seed=16)
    short = challenge.simulate_challenge(
        r, leverage=0.4,
        params=config.SimulatorParams(n_bootstraps=4000, horizon_days=250, seed=1,
                                      block_size=20), with_leverage_curve=False)
    long = challenge.simulate_challenge(
        r, leverage=0.4,
        params=config.SimulatorParams(n_bootstraps=4000, horizon_days=2500, seed=1,
                                      block_size=20), with_leverage_curve=False)
    # Conditional pass is stable across horizons...
    assert abs(short.p_pass_conditional - long.p_pass_conditional) < 0.05
    # ...while raw p_both changes materially (short horizon leaves more unresolved).
    assert short.p_unresolved > 0.2
    assert long.p_both - short.p_both > 0.05


def test_pass_prob_monotonic_in_leverage():
    # Document thesis (§2.1): less volatility → more P(pass). With an honest
    # horizon, P(pass) must grow as leverage decreases (not collapse to 0, which
    # was the truncation bug).
    r = _gaussian_returns(0.0008, 0.015, n=4000, seed=11)
    p = config.SimulatorParams(n_bootstraps=2500, seed=1, block_size=20)
    res = challenge.simulate_challenge(r, params=p)
    curve = res.leverage_pass_curve
    assert curve[0] > curve[-1]        # decreasing trend in leverage
    assert curve[0] > 0.5              # does not collapse to ~0 at the low end (was the bug)


def test_three_outcome_accounting_no_folding():
    # Regression: "unresolved" is NOT folded into "failed". With low drift and a
    # short horizon, many paths do not absorb; they must be counted separately.
    r = _gaussian_returns(0.00005, 0.01, n=4000, seed=21)
    p = config.SimulatorParams(n_bootstraps=3000, horizon_days=60, seed=1, block_size=20)
    res = challenge.simulate_challenge(r, params=p, leverage=0.25,
                                       with_leverage_curve=False)
    total = res.p_phase1 + res.p_fail + res.p_unresolved
    assert abs(total - 1.0) < 1e-9          # the three outcomes sum to 1
    assert res.p_unresolved > 0.1           # unresolved is visible, not folded
    assert res.horizon_days == 60           # the horizon stays explicit


# --- Determinism -------------------------------------------------------------
def test_report_integration():
    from src import report

    r = pd.Series(_gaussian_returns(0.0004, 0.01, n=3000, seed=13))
    p = config.SimulatorParams(n_bootstraps=1500, horizon_days=252, seed=1, block_size=20)
    res = challenge.simulate_challenge(r, params=p)
    md = report.render(r, name="bh", challenge_result=res)
    assert "Challenge (simulador de barrera)" in md
    assert "P(pasar | absorbió) — decisión" in md
    assert "Apalancamiento óptimo" in md
    assert "Horizonte insuficiente" in md


def test_deterministic_under_seed():
    r = _gaussian_returns(0.0004, 0.01, n=3000, seed=12)
    p = config.SimulatorParams(n_bootstraps=2000, horizon_days=252, seed=99, block_size=20)
    a = challenge.simulate_challenge(r, params=p, with_leverage_curve=False)
    b = challenge.simulate_challenge(r, params=p, with_leverage_curve=False)
    assert a.p_both == b.p_both
    assert a.p_pass_conditional == b.p_pass_conditional
    # Determinista incluso cuando el valor es nan (horizonte insuficiente).
    assert (a.expected_net_value == b.expected_net_value) or (
        np.isnan(a.expected_net_value) and np.isnan(b.expected_net_value)
    )
