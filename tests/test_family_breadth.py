"""Tests de la medición de diversificación por familia (N_eff de estrategias, carry proxy)."""

from __future__ import annotations

import numpy as np

from scripts import family_breadth as fb


def test_n_eff_of_independent_is_n():
    assert abs(fb.n_eff(np.eye(3)) - 3.0) < 1e-9


def test_n_eff_collapses_with_correlation():
    # 3 estrategias equicorrelacionadas a 0.9 → N_eff cerca de 1
    c = np.full((3, 3), 0.9); np.fill_diagonal(c, 1.0)
    assert fb.n_eff(c) < 1.4
    # a correlación ~0.09 (lo medido) → N_eff cerca de 3
    c2 = np.full((3, 3), 0.09); np.fill_diagonal(c2, 1.0)
    assert fb.n_eff(c2) > 2.8


def test_carry_weights_respect_gross_cap():
    import pandas as pd
    from src import config
    prices = pd.DataFrame({c: pd.read_parquet(config.DATA_CLEAN / f"{c}.parquet")["close"]
                           for c in fb.FX}).dropna(how="any")
    w = fb.carry_weights(prices)
    gross = w.abs().sum(axis=1)
    assert (gross <= config.MAX_GROSS_EXPOSURE + 1e-6).all()   # respeta el cap de exposición bruta
    assert not w.isna().any().any()
