"""Tests del perfil de volumen (H008, Bloque 3.1)."""

from __future__ import annotations

import numpy as np
import pytest

from src.crypto import volume_profile as vp


def test_poc_is_max_volume_bucket():
    # todo el volumen concentrado en $100 → POC en ese bucket
    prices = np.array([101.0, 102.0, 105.0, 108.0, 250.0])
    qty = np.array([100.0, 100.0, 100.0, 100.0, 1.0])   # bucket [100,110) domina
    p = vp.build_profile(prices, qty, bucket=10.0, va_frac=0.70)
    assert 100.0 <= p.poc <= 110.0


def test_value_area_captures_at_least_70pct():
    rng = np.random.default_rng(0)
    prices = 100.0 + rng.normal(scale=5, size=10000)     # concentrado alrededor de 100
    qty = np.ones(10000)
    p = vp.build_profile(prices, qty, bucket=1.0, va_frac=0.70)
    assert p.va_volume_frac >= 0.70                       # el VA contiene ≥70% del volumen
    assert p.val < p.poc < p.vah                          # POC dentro del VA
    assert p.low <= p.val and p.vah <= p.high             # VA dentro del rango del día


def test_vah_val_within_day_range():
    prices = np.array([50.0, 60.0, 70.0, 80.0, 90.0])
    qty = np.array([1.0, 5.0, 10.0, 5.0, 1.0])           # simétrico, POC en 70
    p = vp.build_profile(prices, qty, bucket=10.0)
    assert p.high == 90.0 and p.low == 50.0
    assert 70.0 <= p.poc <= 80.0
