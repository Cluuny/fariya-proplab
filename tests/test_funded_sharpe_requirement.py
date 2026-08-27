"""Guards del barrido de Sharpe requerido (sobre challenge.py, infra existente)."""

from __future__ import annotations

import numpy as np

from scripts import funded_sharpe_requirement as fr


def test_synth_returns_hit_target_moments():
    # la serie estandarizada tiene EXACTAMENTE (mu_d, sig_d) — sin ruido de Sharpe realizado
    r = fr.synth_returns(0.5, 0.08, 1.0, seed=1)
    sig_d = 0.08 / np.sqrt(fr.TRADING_DAYS)
    mu_d = 0.5 * 0.08 / fr.TRADING_DAYS - fr.swap_drag_daily(1.0)
    assert np.isclose(r.std(ddof=0), sig_d, rtol=1e-9)
    assert np.isclose(r.mean(), mu_d, atol=1e-12)


def test_margin_mult_increases_drag():
    assert fr.swap_drag_daily(1.5) > fr.swap_drag_daily(1.0) > 0


def test_p_exito_monotonic_in_sharpe():
    seed = 12345
    vals = [fr.run_cell(s, 0.08, 1.0, seed + i)["p_exito"] for i, s in enumerate([0.2, 0.5, 0.8, 1.0])]
    # monótono no decreciente (con pequeña tolerancia de muestreo bootstrap)
    for a, b in zip(vals, vals[1:]):
        assert b >= a - 0.03, f"P(éxito) no monótono: {vals}"


def test_burn_probability_low_at_these_vols():
    # el drawdown 10% está lejos vs la vol de una ventana de 21 d → sobrevivir NO es el cuello
    c = fr.run_cell(0.5, 0.08, 1.0, seed=7)
    assert c["p_burn12"] < 0.1
