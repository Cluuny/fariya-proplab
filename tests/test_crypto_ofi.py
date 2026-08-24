"""Tests de Bloque 2: la fórmula OFI (Cont-Kukanov-Stoikov §2.1) y la calibración.

El test de la FÓRMULA es el más importante: e_n calculado a mano vs. la implementación.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.crypto import calibrate, ofi


def _book(rows):
    """rows: list of (update_id, PB, qB, PA, qA, t). Returns a sorted bookTicker df."""
    cols = ["update_id", "best_bid_price", "best_bid_qty",
            "best_ask_price", "best_ask_qty", "transaction_time"]
    df = pd.DataFrame(rows, columns=cols)
    df["event_time"] = df["transaction_time"]
    return df.sort_values(["transaction_time", "update_id"]).reset_index(drop=True)


def test_ofi_event_formula_by_hand():
    # obs0: PB100.0 qB5 PA100.1 qA4 ; obs1: bid qty 5->8 (prices same) ; obs2: both prices up
    df = _book([
        (1, 100.0, 5.0, 100.1, 4.0, 1000),
        (2, 100.0, 8.0, 100.1, 4.0, 1001),
        (3, 100.1, 2.0, 100.2, 6.0, 1002),
    ])
    e, t, mid = ofi.compute_events(df)
    # e_1 = 1{100.0>=100.0}*8 - 1{100.0<=100.0}*5 - 1{100.1<=100.1}*4 + 1{100.1>=100.1}*4 = 8-5-4+4 = 3
    # e_2 = 1{100.1>=100.0}*2 - 1{100.1<=100.0}*8 - 1{100.2<=100.1}*6 + 1{100.2>=100.1}*4 = 2-0-0+4 = 6
    assert np.allclose(e, [3.0, 6.0])
    assert list(t) == [1001, 1002]
    assert np.allclose(mid, [(100.0 + 100.1) / 2, (100.1 + 100.2) / 2])


def test_ofi_pure_bid_add_is_positive():
    # sólo se añade tamaño al bid, precios quietos -> e = +ΔqB
    df = _book([(1, 50.0, 2.0, 50.1, 3.0, 0), (2, 50.0, 9.0, 50.1, 3.0, 1)])
    e, _, _ = ofi.compute_events(df)
    assert e[0] == pytest.approx(7.0)     # 9 - 2 (ask sin cambio: -3+3=0)


def test_ofi_price_up_uses_previous_ask_size():
    # bid price sube: e suma qB_n (nuevo bid) y, por el ask sin cambio, +qA_{n-1}-qA_n=0
    df = _book([(1, 10.0, 4.0, 10.1, 5.0, 0), (2, 10.1, 6.0, 10.2, 7.0, 1)])
    e, _, _ = ofi.compute_events(df)
    # e = 1{10.1>=10.0}*6 - 1{10.1<=10.0}*4 - 1{10.2<=10.1}*7 + 1{10.2>=10.1}*5 = 6-0-0+5 = 11
    assert e[0] == pytest.approx(11.0)


def test_build_grid_bins_and_dP():
    df = _book([
        (1, 100.0, 5.0, 100.1, 4.0, 0),
        (2, 100.0, 8.0, 100.1, 4.0, 3000),      # bin 0 (0-10s)
        (3, 100.1, 2.0, 100.2, 6.0, 12000),     # bin 1 (10-20s)
    ])
    grid = ofi.build_grid(df, dt_s=10, tick=0.1)
    # dP entre bins: mid bin0=100.05 (last=obs at t=3000), bin1 mid=100.15 -> ΔP=(0.10)/0.1=1 tick
    assert len(grid) == 1                        # el primer bin no tiene dP (diff)
    assert grid["dP"].iloc[0] == pytest.approx(1.0, abs=1e-6)


def test_ols_white_recovers_known_line():
    rng = np.random.default_rng(0)
    x = rng.normal(size=500)
    y = 2.0 + 0.5 * x + rng.normal(scale=1e-9, size=500)   # casi sin ruido
    r = calibrate.ols_white(y, x)
    assert r["a"] == pytest.approx(2.0, abs=1e-3)
    assert r["b"] == pytest.approx(0.5, abs=1e-3)
    assert r["r2"] > 0.999


def test_calibrate_linear_data_high_r2():
    # construir un grid sintético donde ΔP = OFI/(2D) exactamente -> R² ~ 1, β>0
    rng = np.random.default_rng(1)
    n = 2000
    t = (np.arange(n) * 10_000).astype("int64")   # 10s grid, cubre >1 media hora
    ofi_vals = rng.normal(scale=50, size=n)
    D = 10.0
    dP = ofi_vals / (2 * D)
    grid = pd.DataFrame({"OFI": ofi_vals, "dP": dP, "depth": D, "mid": 0.0}, index=t)
    res = calibrate.calibrate(grid)
    assert res.mean_r2_ofi > 0.99
    assert res.mean_beta == pytest.approx(1 / (2 * D), abs=1e-6)


def test_trade_imbalance_sign_convention():
    agg = pd.DataFrame({
        "transact_time": [0, 1, 2],
        "quantity": [1.0, 2.0, 3.0],
        "is_buyer_maker": [False, True, False],   # buy-aggressor, sell-aggressor, buy-aggressor
    })
    ti = ofi.trade_imbalance(agg, dt_s=10)
    # todos caen en el bin 0: +1 -2 +3 = +2
    assert ti.iloc[0] == pytest.approx(2.0)
