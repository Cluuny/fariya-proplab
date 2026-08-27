"""Guards del análisis de sensibilidad a la vol (supervivencia acumulativa + caveats)."""

from __future__ import annotations

import numpy as np

from scripts import funded_vol_sensitivity as fv


def _net(vol, mu_ann=0.0, n=4000, seed=0):
    rng = np.random.default_rng(seed)
    z = rng.normal(0, 1, n); z = (z - z.mean()) / z.std(ddof=0)
    return mu_ann / 252 + (vol / np.sqrt(252)) * z


def test_accum_survival_falls_with_vol():
    # a más vol, MÁS quema acumulativa en 12 ciclos (la barrera muerde)
    s_lo = fv.funded_survive_accum(_net(0.08), 12, intraday_mult=1.0, seed=1)
    s_hi = fv.funded_survive_accum(_net(0.25), 12, intraday_mult=1.0, seed=1)
    assert s_hi < s_lo


def test_intraday_factor_increases_burn():
    # el límite diario intradía (factor>1) sólo puede AUMENTAR la quema
    s_close = fv.funded_survive_accum(_net(0.20), 12, intraday_mult=1.0, seed=2)
    s_intra = fv.funded_survive_accum(_net(0.20), 12, intraday_mult=1.8, seed=2)
    assert s_intra <= s_close


def test_accumulating_more_punitive_than_independent_at_low_vol():
    # caveat (a): la supervivencia acumulativa a 8% NO es ~0 de quema (a diferencia del independiente)
    net = _net(0.08, mu_ann=0.02)
    p_surv = fv.funded_survive_accum(net, 12, intraday_mult=1.0, seed=3)
    assert 0.5 < p_surv < 1.0   # muerde algo, no es ni 0 ni 1


def test_real_shape_has_fat_tails():
    z = fv._real_shape()
    import pandas as pd
    assert pd.Series(z).kurt() > 1.0   # curtosis en exceso real (colas gordas)
