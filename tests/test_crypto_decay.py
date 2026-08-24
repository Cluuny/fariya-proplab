"""Tests de Bloque B: la lógica de la curva de decaimiento y el cruce con costes."""

from __future__ import annotations

import numpy as np
import pytest

from src.crypto import cost_model, decay


def _synth_events(n=20000, ic=0.3, seed_mult=1):
    """Genera (e, t, mid) donde el OFI de un bin de 1s predice el return del siguiente con
    correlación ~ic. t en ms, un evento por segundo para que bins de 1s tengan 1 evento."""
    # deterministic pseudo-random sin RNG global
    idx = np.arange(n)
    ofi = np.sin(idx * 0.7 * seed_mult) * 50 + np.cos(idx * 1.3) * 30
    noise = np.sin(idx * 2.1 + 0.5) * 100
    # return del bin siguiente correlacionado con ofi del bin actual
    fwd = ic * (ofi / ofi.std()) + (1 - ic) * (noise / noise.std())
    mid = 100.0 + np.cumsum(fwd) * 0.001
    t = (idx * 1000).astype("int64")   # 1 evento/segundo
    e = ofi
    return e, t, mid


def test_decay_detects_predictive_signal():
    ev = _synth_events(ic=0.4)
    rows = decay.decay_curve([ev], horizons=[1, 5, 10])
    r1 = next(r for r in rows if r.horizon_s == 1)
    assert r1.r2_pred > 0.02            # hay señal predictiva a 1s por construcción
    assert abs(r1.ic_pred) > 0.1


def test_decay_no_signal_is_near_zero():
    # ruido puro: sin correlación con el futuro
    n = 20000
    idx = np.arange(n)
    e = np.sin(idx * 0.7) * 50
    mid = 100.0 + np.cumsum(np.cos(idx * 3.3)) * 0.001   # no relacionado con e
    t = (idx * 1000).astype("int64")
    rows = decay.decay_curve([(e, t, mid)], horizons=[1, 10])
    assert rows[0].r2_pred < 0.02       # ~cero predictibilidad


def test_rt_per_day_and_floor_rise_at_short_horizons():
    ev = _synth_events()
    rows = decay.decay_curve([ev], horizons=[1, 3600])
    r_fast = rows[0]; r_slow = rows[1]
    assert r_fast.rt_per_day == 86400          # 1s → 86400 rt/día
    assert r_slow.rt_per_day == 24             # 1h → 24 rt/día
    # el listón sube brutalmente a alta frecuencia
    assert r_fast.floor_maker > r_slow.floor_maker > cost_model.UMBRAL_NETO


def test_implied_sharpe_uses_breadth():
    # a igualdad de IC, más apuestas (horizonte corto) → mayor Sharpe implícito
    s_fast = decay._implied_sharpe(0.01, 1)
    s_slow = decay._implied_sharpe(0.01, 3600)
    assert s_fast > s_slow > 0


def _row(h, implied, lo, hi, floor_m):
    return decay.HorizonRow(
        horizon_s=h, r2_contemp=0.5, r2_pred=0.01, ic_pred=0.1, ic_lo=0.05, ic_hi=0.15,
        n_indep=1000, implied_sharpe=implied, implied_sharpe_lo=lo, implied_sharpe_hi=hi,
        rt_per_day=86400 / h, floor_maker=floor_m, floor_taker=floor_m * 2,
        gap_maker=implied - floor_m, gap_taker=implied - floor_m * 2)


def test_verdict_closes_when_no_horizon_beats_floor():
    # todos por debajo de su listón (IC alto no basta si el listón es aún más alto)
    rows = [_row(1, 50, 40, 60, 200), _row(3600, 0.3, 0.1, 0.5, 0.65)]
    v = decay.verdict(rows)
    assert v["estado"] == "ORDER_FLOW_CERRADO"
    assert v["mejor_gap_maker"] < 0


def test_verdict_real_signal_when_lower_ci_clears_floor():
    rows = [_row(3600, 2.0, 1.2, 2.8, 0.65)]   # IC inferior (1.2) > listón (0.65)
    assert decay.verdict(rows)["estado"] == "INDICIO_REAL"


def test_verdict_indeterminate_when_ci_crosses_floor():
    rows = [_row(3600, 1.0, 0.4, 1.6, 0.65)]   # listón 0.65 dentro de [0.4, 1.6]
    assert decay.verdict(rows)["estado"] == "INDETERMINADO"
