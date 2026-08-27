"""Tests del cribado aritmético (Deflated Sharpe, IC, amplitud efectiva)."""

from __future__ import annotations

import math

from src.pipeline import candidate_screen as cs


def test_sharpe_se_decreases_with_n():
    assert cs.sharpe_se(0.5, 100) > cs.sharpe_se(0.5, 400)
    # valor conocido: SE(0)=√(1/n)
    assert math.isclose(cs.sharpe_se(0.0, 100), 0.1, rel_tol=1e-9)


def test_sharpe_se_annual_matches_manual():
    # 0.55 anual, 27.5 años, 12/año → ~0.19 (Lo, reanualizado)
    se = cs.sharpe_se_annual(0.55, 27.5, 12)
    assert 0.18 < se < 0.20


def test_sharpe_ci_contains_liston_is_irresoluble():
    se = cs.sharpe_se_annual(0.55, 27.5, 12)
    lo, hi = cs.sharpe_ci(0.55, se)
    assert lo <= 0.44 <= hi   # el listón cae dentro → irresoluble


def test_expected_max_sharpe_grows_with_trials():
    se = 0.19
    assert cs.expected_max_sharpe(10, se) < cs.expected_max_sharpe(100, se)
    # a N grande, la suerte alcanza el listón 0.44
    assert cs.expected_max_sharpe(100, se) >= 0.44


def test_effective_breadth_collapses_with_correlation():
    # 9 sectores a ρ=0.75 → ~1.3 (casi una apuesta)
    b = cs.effective_breadth(9, 0.75)
    assert 1.2 < b < 1.4
    # independientes (ρ=0) → N completo
    assert math.isclose(cs.effective_breadth(9, 0.0), 9.0)


def test_deflation_screen_flags_liston_reached():
    se = cs.sharpe_se_annual(0.55, 27.5, 12)
    rows = cs.deflation_screen(0.55, se, 0.44, [10, 100])
    assert not rows[0]["umbral_sobre_liston"]   # N=10 no alcanza el listón
    assert rows[1]["umbral_sobre_liston"]        # N=100 sí
