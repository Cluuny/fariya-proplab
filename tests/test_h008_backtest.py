"""Tests del simulador de H008 Bloque 4 (fills al toque, salidas, comisión/funding)."""

from __future__ import annotations

import numpy as np

from src.crypto import h008_backtest as bt


def _bars(rows):
    # rows: (t_ms, high, low, close)
    return np.array(rows, float)


def test_short_hits_target():
    # entra en 100 (toca), luego baja al objetivo 90
    b = _bars([(0, 100, 99, 99.5), (60000, 100.5, 100, 100), (120000, 95, 90, 90)])
    tr = bt.simulate(b, entry_level=100.0, target=90.0, va_range=10.0, direction="short")
    assert tr.filled and tr.exit_type == "target"
    # gross = (100-90)/100 = 0.10; menos comisión maker+maker (0.0004)
    assert tr.ret_net > 0.09


def test_short_hits_stop():
    b = _bars([(0, 100, 99, 100), (60000, 111, 100, 111)])   # sube al stop 110
    tr = bt.simulate(b, entry_level=100.0, target=90.0, va_range=10.0, direction="short")
    assert tr.filled and tr.exit_type == "stop"
    assert tr.ret_net < 0                                     # pérdida (stop) + comisión taker


def test_no_fill_if_not_touched():
    b = _bars([(0, 95, 90, 92), (60000, 96, 93, 94)])        # nunca llega a 100
    tr = bt.simulate(b, entry_level=100.0, target=90.0, va_range=10.0, direction="short")
    assert not tr.filled


def test_fill_bps_stricter_blocks_touch():
    # toca 100 justo pero no cruza 5 bps → con fill_bps=5 no llena
    b = _bars([(0, 100.0, 99, 99.5), (60000, 100.02, 100, 100)])
    assert bt.simulate(b, 100.0, 90.0, 10.0, "short", fill_bps=0).filled
    assert not bt.simulate(b, 100.0, 90.0, 10.0, "short", fill_bps=5).filled


def test_funding_crossing_detected():
    # episodio que cruza el corte 08:00 UTC (28800000 ms desde medianoche)
    b = _bars([(28700000, 100, 99, 100), (28900000, 95, 90, 90)])
    tr = bt.simulate(b, 100.0, 90.0, 10.0, "short")
    assert tr.crossed_funding


def test_sharpe_active_scales_with_breadth():
    r = [0.01, -0.005, 0.008, -0.002, 0.006]
    s1 = bt.sharpe_active(r, 50)
    s2 = bt.sharpe_active(r, 200)
    assert s2 > s1 > 0                                        # más apuestas/año → mayor Sharpe
