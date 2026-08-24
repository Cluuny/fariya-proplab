"""Tests de Bloque 3: modelo de costes cripto (comisión maker/taker, funding evitable)."""

from __future__ import annotations

import pytest

from src.crypto import cost_model as cm


def test_commission_maker_vs_taker():
    assert cm.comision_round_trip(0.0) == pytest.approx(2 * cm.TAKER_FEE)   # 0.0010
    assert cm.comision_round_trip(1.0) == pytest.approx(2 * cm.MAKER_FEE)   # 0.0004
    # maker es menos de la mitad que taker
    assert cm.comision_round_trip(1.0) < cm.comision_round_trip(0.0) / 2 * 1.01
    with pytest.raises(ValueError):
        cm.comision_round_trip(1.5)


def test_cost_per_unit_of_risk_reproduces_pivot():
    # taker ≈ 0.033 (razón del pivote), maker ≈ 0.013, ambos por debajo de MES 0.063
    assert cm.coste_por_unidad_riesgo(0.0) == pytest.approx(0.032, abs=0.003)
    assert cm.coste_por_unidad_riesgo(1.0) == pytest.approx(0.013, abs=0.003)
    assert cm.coste_por_unidad_riesgo(0.0) < 0.063     # favorable vs MES


def test_funding_is_avoidable():
    assert cm.funding_anual(0) == 0.0                  # day trader que evita cortes → CERO
    assert cm.funding_anual(3) == pytest.approx(3 * 365 * cm.FUNDING_PER_INTERVAL_DEFAULT)
    assert cm.funding_anual(3) > cm.funding_anual(1) > 0
    with pytest.raises(ValueError):
        cm.funding_anual(4)                            # sólo 3 cortes/día


def test_required_rises_with_trades_and_falls_with_maker():
    r_taker_1 = cm.sharpe_bruto_requerido_cripto(1, fraccion_maker=0.0)
    r_taker_5 = cm.sharpe_bruto_requerido_cripto(5, fraccion_maker=0.0)
    r_maker_1 = cm.sharpe_bruto_requerido_cripto(1, fraccion_maker=1.0)
    assert r_taker_5 > r_taker_1 > cm.UMBRAL_NETO      # más rotación → más listón
    assert r_maker_1 < r_taker_1                        # maker baja el listón


def test_funding_adds_to_required():
    sin = cm.sharpe_bruto_requerido_cripto(2, fraccion_maker=1.0, cruces_funding_por_dia=0)
    con = cm.sharpe_bruto_requerido_cripto(2, fraccion_maker=1.0, cruces_funding_por_dia=3)
    assert con > sin
    # el ahorro por evitar funding es exactamente funding_anual/vol
    assert con - sin == pytest.approx(cm.funding_anual(3) / cm.VOL_ANUAL_BTC, rel=1e-9)


def test_maker_low_frequency_no_funding_is_competitive():
    # la celda favorable: maker, 1 round-trip/día, sin funding ≈ CFD swing 0.64
    r = cm.sharpe_bruto_requerido_cripto(1, fraccion_maker=1.0, cruces_funding_por_dia=0)
    assert 0.60 < r < 0.70


def test_tabla_shape():
    rows = cm.tabla_requerido()
    assert len(rows) == 4 * 3 * 2                       # trades × maker × funding
    assert {r["funding_en_corte"] for r in rows} == {"no", "sí"}
