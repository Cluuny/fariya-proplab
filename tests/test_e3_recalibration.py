"""Tests de la recalibración de E3: factor de degradación, familia_de_riesgo, métricas alternativas."""

from __future__ import annotations

from src import costs_model
from src.pipeline import estimate, triage_costs


def test_factor_degradacion_haircut():
    assert costs_model.FACTOR_DEGRADACION == 0.35
    assert costs_model.bruto_efectivo(1.0) == 0.35
    assert costs_model.bruto_efectivo(2.0) == 0.70


def test_e3_applies_degradation_sectoral_dies():
    # el Sectoral: reportado 0.55 → efectivo 0.19 < listón → reject (antes pasaba con 0.55)
    v = triage_costs.triage_costs({"frecuencia": "EOD", "duty_cycle_estimado": 0.15,
                                   "bruto_reportado": 0.55})
    assert v.decision == "reject" and "efectivo" in v.razon


def test_e3_keep_needs_high_reported():
    # E3 evalúa AMBOS vehículos; el más fácil es futuros (req 0.42 a duty 1.0) → hace falta
    # reportado > 0.42/0.35 ≈ 1.20 (coincide con el ~1.15 del bloque). CFD (0.64) exige ~1.83.
    assert triage_costs.triage_costs({"frecuencia": "EOD", "duty_cycle_estimado": 1.0,
                                      "bruto_reportado": 1.0}).decision == "reject"   # 0.35 < 0.42
    assert triage_costs.triage_costs({"frecuencia": "EOD", "duty_cycle_estimado": 1.0,
                                      "bruto_reportado": 2.0}).decision == "keep"     # 0.70 > 0.64


def test_familia_de_riesgo_classification():
    fam = estimate.estimate_familia_de_riesgo
    assert fam({"abstract": "time-series momentum across global futures"}) == "trend"
    assert fam({"abstract": "a currency carry trade, long high-yield currencies"}) == "carry"
    assert fam({"abstract": "short-horizon mean reversion, betting against the previous candle"}) == "reversion"
    assert fam({"abstract": "the turn-of-the-month seasonal anomaly"}) == "estacionalidad"
    # 'carry' como VERBO no debe clasificar como carry
    assert fam({"abstract": "pairs carry significant directional reversal"}) == "reversion"


def test_metric_fallback_ret_vol_and_ir_and_tstat():
    ex = estimate.extract_bruto_estimado
    # ret/vol
    b, c = ex({"abstract": "the strategy earns 12% annualized returns with volatility of 15%"})
    assert b is not None and abs(b - 0.8) < 0.01 and "→" in c
    # information ratio
    b2, c2 = ex({"abstract": "an information ratio of 0.9 out of sample"})
    assert b2 == 0.9 and "information ratio" in c2
    # ausente → None
    assert ex({"abstract": "we document a robust effect"}) == (None, None)


def test_direct_sharpe_takes_precedence_over_fallback():
    b, c = estimate.extract_bruto_estimado(
        {"abstract": "Sharpe ratio of 1.1; also 20% return and 10% vol"})
    assert b == 1.1  # el Sharpe directo gana, no el ret/vol (que daría 2.0)
