"""Tests del estimador determinista (estación 2.5): frecuencia, duty, Sharpe, prioridad."""

from __future__ import annotations

from src.pipeline import estimate


def _c(titulo="", abstract="", tipo_de_fuente="preprint"):
    return {"titulo": titulo, "abstract": abstract, "tipo_de_fuente": tipo_de_fuente}


# ---------------------------------------------------------------- frecuencia
def test_frecuencia_orderbook():
    assert estimate.estimate_frecuencia("we study order flow imbalance in the limit order book") == "orderbook"


def test_frecuencia_intraday():
    assert estimate.estimate_frecuencia("an intraday momentum strategy on 5-minute bars") == "intraday_bar"


def test_frecuencia_eod_default():
    assert estimate.estimate_frecuencia("a monthly time-series momentum strategy on futures") == "EOD"


# ---------------------------------------------------------------- duty
def test_duty_low_for_calendar():
    assert estimate.estimate_duty("the turn-of-the-month effect in equity indices") == estimate._LOW_DUTY_VALUE


def test_duty_full_by_default():
    assert estimate.estimate_duty("trend following across global futures") == 1.0


# ---------------------------------------------------------------- extracción del Sharpe
def test_extract_sharpe_with_value():
    val, cita = estimate.extract_bruto_reportado(_c(abstract="The strategy earns a Sharpe ratio of 1.35 net of costs."))
    assert val == 1.35 and cita is not None and "abstract" in cita


def test_extract_sharpe_absent_is_none():
    val, cita = estimate.extract_bruto_reportado(_c(abstract="We document a robust predictive relationship."))
    assert val is None and cita is None   # ANTI-ALUCINACIÓN: ausencia → null, no cero


def test_extract_sharpe_takes_max_plausible():
    val, _ = estimate.extract_bruto_reportado(_c(abstract="Sharpe of 0.6 gross; Sharpe ratio of 1.8 after leverage."))
    assert val == 1.8


def test_extract_sharpe_ignores_out_of_range():
    # "Sharpe ratio of 2019" (un año travestido) queda fuera del rango plausible
    val, _ = estimate.extract_bruto_reportado(_c(abstract="Since Sharpe ratio of 2019 studies..."))
    assert val is None


# ---------------------------------------------------------------- estimate_fields
def test_estimate_fields_eod_has_duty_no_trades():
    f = estimate.estimate_fields(_c(abstract="monthly carry strategy in FX, Sharpe ratio of 0.9"))
    assert f["frecuencia"] == "EOD" and f["duty_cycle_estimado"] == 1.0
    assert f["bruto_reportado"] == 0.9 and "trades_por_dia_estimado" not in f


def test_estimate_fields_intraday_has_trades_contrato():
    f = estimate.estimate_fields(_c(abstract="high-frequency order flow imbalance on Nasdaq futures"))
    assert f["frecuencia"] == "orderbook" and f["duty_cycle_estimado"] is None
    assert f["trades_por_dia_estimado"] > 0 and f["contrato_ref"] == "NQ"


# ---------------------------------------------------------------- prioridad
def test_priority_prefers_clearing_gross_and_arbitrated():
    hi = estimate.priority_score({"bruto_reportado": 1.2, "bruto_requerido_cfd": 0.64,
                                  "tipo_de_fuente": "paper_arbitrado", "frecuencia": "EOD"})
    lo = estimate.priority_score({"bruto_reportado": None, "bruto_requerido_cfd": 0.64,
                                  "tipo_de_fuente": "blog", "frecuencia": "orderbook"})
    assert hi > lo


def test_priority_no_negative_from_missing_margin():
    s = estimate.priority_score({"bruto_reportado": 0.1, "bruto_requerido_cfd": 0.64,
                                 "tipo_de_fuente": "preprint", "frecuencia": "EOD"})
    assert s >= 1.0   # margen negativo se recorta a 0, no resta


# ---------------------------------------------------------------- arXiv query builder (E1)
def test_arxiv_query_url_encodes_phrase():
    from src.pipeline import discover
    url = discover.arxiv_query_url(cats=("q-fin.TR",), terms=("order flow imbalance",), max_results=3)
    # comillas de frase → %22, espacios intra-frase → '+', y AND-scope a la categoría
    assert 'all:%22order+flow+imbalance%22' in url
    assert '+AND+' in url and '"' not in url and '%20' not in url


def test_arxiv_query_url_no_terms_is_plain_or():
    from src.pipeline import discover
    url = discover.arxiv_query_url(cats=("q-fin.PM", "q-fin.ST"), max_results=5)
    assert url.count("cat:") == 2 and "+AND+" not in url and "all:" not in url


# ------------------------------------------- E2 falsabilidad: sin falsos positivos de acrónimos
def test_operability_acronym_not_substring_false_positive():
    from src.pipeline import triage_operability as top
    # "predict"/"explicit"/"restrict" contienen "ict" pero NO son ICT/SMC → no deben rechazar
    v = top.triage_operability({"titulo": "Harvesting the volatility risk premium",
        "abstract": "We predict returns with explicit signals and a trend-following rule."})
    assert v.categoria != "falsabilidad"
    # un ICT real SÍ se rechaza (límite de palabra lo respeta)
    v2 = top.triage_operability({"titulo": "ICT order blocks and fair value gaps",
        "abstract": "We trade order blocks drawn on the chart."})
    assert v2.decision == "reject" and v2.categoria == "falsabilidad"


def test_extract_sharpe_number_before_word():
    # "0.55 Sharpe ratio" (número ANTES de Sharpe) — hallado en la run 002 (momentum sectorial)
    val, cita = estimate.extract_bruto_reportado(
        {"abstract": "delivers 5.99% annualized return at a 0.55 Sharpe ratio for the long-short variant"})
    assert val == 0.55 and "abstract" in cita
