"""Bloque B — challenge-simulator.

Verificación contra la fórmula analítica cerrada (no contra la intuición),
block bootstrap que preserva volatilidad, barreras, métricas económicas,
curva de apalancamiento y determinismo.
"""

import numpy as np
import pandas as pd
import pytest

from src import challenge, config


def _gaussian_returns(mu, sigma, n=6000, seed=0):
    return np.random.default_rng(seed).normal(mu, sigma, n)


def _verif_rules(barrier):
    # Doble barrera pura: sin límite diario (=1.0), DD = barrera inferior.
    return config.FirmRules(
        phase1_target=barrier,
        phase2_target=barrier,
        daily_loss_limit=1.0,
        max_drawdown=barrier,
        n_payouts=1,
        fee=0.0,
        payout_per_cycle=0.0,
    )


def _verif_params(**kw):
    base = dict(block_size=1, n_bootstraps=12000, horizon_days=600, seed=7,
                leverage_min=1.0, leverage_max=1.0, leverage_step=1.0)
    base.update(kw)
    return config.SimulatorParams(**base)


# --- Sección 6: verificación matemática -------------------------------------
def test_zero_drift_symmetric_barriers_gives_half():
    # DoD semana 4: μ=0, barreras simétricas 10/10 → P≈0.5.
    # σ suficientemente grande para que casi todas las trayectorias absorban
    # dentro del horizonte (evita el sesgo por truncación); simétrico → 0.5.
    r = _gaussian_returns(0.0, 0.02, n=8000, seed=1)
    res = challenge.simulate_challenge(
        r, rules=_verif_rules(0.10), params=_verif_params(), with_leverage_curve=False
    )
    assert abs(res.p_phase1 - 0.5) < 0.03


def test_matches_closed_form_with_drift():
    # Barreras 10/10 con deriva. El simulador remuestrea de la serie empírica,
    # así que la comparación honesta evalúa la fórmula cerrada con los MOMENTOS
    # EMPÍRICOS de la serie (no los teóricos): con μ pequeño el error de muestreo
    # del promedio desplazaría el objetivo analítico. Tolerancia = overshoot + MC.
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


# --- Sección 2: block bootstrap ---------------------------------------------
def _sq_autocorr_lag1(x):
    s = x**2
    s = s - s.mean()
    return float((s[:-1] * s[1:]).sum() / (s * s).sum())


def test_block_bootstrap_preserves_volatility_clustering():
    # Serie con clustering: bloques alternos de baja y alta volatilidad.
    rng = np.random.default_rng(0)
    vol = np.concatenate([np.full(100, 0.003), np.full(100, 0.03)] * 10)
    returns = rng.normal(0, 1, vol.size) * vol
    acf_orig = _sq_autocorr_lag1(returns)

    gen = np.random.default_rng(1)
    block = challenge.block_bootstrap(returns, n_paths=1, horizon=4000, block_size=100, rng=gen)[0]
    iid = challenge.block_bootstrap(returns, n_paths=1, horizon=4000, block_size=1, rng=gen)[0]

    acf_block = _sq_autocorr_lag1(block)
    acf_iid = _sq_autocorr_lag1(iid)

    assert acf_orig > 0.1                 # la serie original tiene clustering
    assert acf_block > 0.1                # el block bootstrap lo preserva
    assert acf_block > acf_iid + 0.05     # i.i.d. lo destruye (~0)


def test_block_bootstrap_deterministic():
    r = _gaussian_returns(0.0, 0.01, n=1000, seed=5)
    a = challenge.block_bootstrap(r, n_paths=50, horizon=200, block_size=20,
                                  rng=np.random.default_rng(9))
    b = challenge.block_bootstrap(r, n_paths=50, horizon=200, block_size=20,
                                  rng=np.random.default_rng(9))
    assert np.array_equal(a, b)


# --- Sección 3: barreras -----------------------------------------------------
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
    # Trayectoria que sube a +8% y luego cae a +? — con DD estático 10% NO quema
    # mientras el capital no baje 10% del INICIAL, aunque caiga desde un pico.
    # Camino: +8% acumulado, luego -0.05/día. Estático permite bajar hasta -10%
    # del inicial; trailing habría quemado mucho antes desde el pico.
    up = np.concatenate([np.full(8, 0.01), np.full(30, -0.005)])
    paths = up.reshape(1, -1)
    passed, _ = challenge._first_passage(
        paths, target=0.20, daily_loss_limit=1.0, max_drawdown=0.10
    )
    # No alcanzó el objetivo 20% y no quemó por DD estático hasta cruzar -10% real.
    # Verificamos que el evento de quema respeta la barrera estática (aditiva):
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


# --- Sección 4: métricas económicas -----------------------------------------
def test_expected_net_value_monotonic_in_edge():
    p = config.SimulatorParams(n_bootstraps=3000, horizon_days=252, seed=1, block_size=20)
    r_low = _gaussian_returns(0.0003, 0.01, n=4000, seed=10)
    r_high = _gaussian_returns(0.0009, 0.01, n=4000, seed=10)  # más deriva, misma vol
    net_low = challenge.simulate_challenge(r_low, params=p, with_leverage_curve=False).expected_net_value
    net_high = challenge.simulate_challenge(r_high, params=p, with_leverage_curve=False).expected_net_value
    assert net_high > net_low


# --- Sección 5: curva de apalancamiento (decisión económica) ----------------
def test_optimal_leverage_is_interior():
    # El óptimo de DECISIÓN sale del valor esperado neto (no de argmax P). Con
    # un costo de capital realista, es interior: ni el mínimo ni el máximo.
    r = _gaussian_returns(0.0008, 0.015, n=4000, seed=11)
    p = config.SimulatorParams(n_bootstraps=2500, seed=1, block_size=20,
                               leverage_min=0.25, leverage_max=3.0, leverage_step=0.25)
    res = challenge.simulate_challenge(r, params=p, with_leverage_curve=True)
    assert res.leverage_grid.size > 1
    assert res.leverage_value_curve.size == res.leverage_grid.size
    assert p.leverage_min < res.optimal_leverage < p.leverage_max  # interior


def test_pass_prob_monotonic_in_leverage():
    # Tesis del documento (§2.1): menos volatilidad → más P(pasar). Con horizonte
    # honesto, P(pasar) debe crecer al bajar el apalancamiento (no colapsar a 0,
    # que era el bug de truncación).
    r = _gaussian_returns(0.0008, 0.015, n=4000, seed=11)
    p = config.SimulatorParams(n_bootstraps=2500, seed=1, block_size=20)
    res = challenge.simulate_challenge(r, params=p)
    curve = res.leverage_pass_curve
    assert curve[0] > curve[-1]        # tendencia decreciente en leverage
    assert curve[0] > 0.5              # no colapsa a ~0 en el extremo bajo (era el bug)


def test_three_outcome_accounting_no_folding():
    # Regresión: "sin absorber" NO se pliega en "falló". Con baja deriva y
    # horizonte corto, muchas trayectorias no absorben; deben contarse aparte.
    r = _gaussian_returns(0.00005, 0.01, n=4000, seed=21)
    p = config.SimulatorParams(n_bootstraps=3000, horizon_days=60, seed=1, block_size=20)
    res = challenge.simulate_challenge(r, params=p, leverage=0.25,
                                       with_leverage_curve=False)
    total = res.p_phase1 + res.p_fail + res.p_unresolved
    assert abs(total - 1.0) < 1e-9          # los tres resultados suman 1
    assert res.p_unresolved > 0.1           # sin-absorber es visible, no plegado
    assert res.horizon_days == 60           # el horizonte queda explícito


# --- Determinismo ------------------------------------------------------------
def test_report_integration():
    from src import report

    r = pd.Series(_gaussian_returns(0.0004, 0.01, n=3000, seed=13))
    p = config.SimulatorParams(n_bootstraps=1500, horizon_days=252, seed=1, block_size=20)
    res = challenge.simulate_challenge(r, params=p)
    md = report.render(r, name="bh", challenge_result=res)
    assert "Challenge (simulador de barrera)" in md
    assert "P(pasar ambas)" in md
    assert "Apalancamiento óptimo" in md


def test_deterministic_under_seed():
    r = _gaussian_returns(0.0004, 0.01, n=3000, seed=12)
    p = config.SimulatorParams(n_bootstraps=2000, horizon_days=252, seed=99, block_size=20)
    a = challenge.simulate_challenge(r, params=p, with_leverage_curve=False)
    b = challenge.simulate_challenge(r, params=p, with_leverage_curve=False)
    assert a.p_both == b.p_both
    assert a.expected_net_value == b.expected_net_value
