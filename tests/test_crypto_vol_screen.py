"""Test de la función pura de amplitud del cribado de vol (n_eff)."""

from __future__ import annotations

import numpy as np

from scripts import crypto_vol_screen as cvs


def test_n_eff_independent_and_correlated():
    assert abs(cvs.n_eff(np.eye(4)) - 4.0) < 1e-9
    c = np.full((4, 4), 0.9); np.fill_diagonal(c, 1.0)
    assert cvs.n_eff(c) < 1.5   # muy correlacionadas → casi una apuesta
