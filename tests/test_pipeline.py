"""Tests del esqueleto del pipeline de investigación (estaciones 1-3 + esquema + backfill)."""

from __future__ import annotations

import pytest

from src import costs_model
from src.pipeline import backfill, db, discover, learning_report
from src.pipeline import triage_costs, triage_operability


@pytest.fixture
def conn():
    c = db.connect(":memory:")
    db.init_db(c)
    yield c
    c.close()


# --------------------------------------------------------------------- esquema
def test_init_and_upsert_roundtrip(conn):
    db.upsert(conn, {
        "id": "X1", "titulo": "t", "clase_de_dato": "precio",
        "datos_requeridos": ["precio_ohlc"], "operable_en_prop": True,
    })
    row = db.get(conn, "X1")
    assert row["titulo"] == "t"
    assert row["operable_en_prop"] == 1          # bool → int
    assert row["datos_requeridos"] == '["precio_ohlc"]'  # list → JSON


def test_upsert_updates_not_duplicates(conn):
    db.upsert(conn, {"id": "X1", "titulo": "t1"})
    db.upsert(conn, {"id": "X1", "titulo": "t2"})
    assert conn.execute("SELECT COUNT(*) FROM hipotesis").fetchone()[0] == 1
    assert db.get(conn, "X1")["titulo"] == "t2"


def test_upsert_requires_id(conn):
    with pytest.raises(ValueError):
        db.upsert(conn, {"titulo": "no id"})


def test_next_in_queue_orders_by_priority(conn):
    db.upsert(conn, {"id": "A", "titulo": "a", "estado": "en_cola", "score_prioridad": 0.2})
    db.upsert(conn, {"id": "B", "titulo": "b", "estado": "en_cola", "score_prioridad": 0.9})
    db.upsert(conn, {"id": "C", "titulo": "c", "estado": "muerta", "score_prioridad": 5.0})
    assert db.next_in_queue(conn)["id"] == "B"     # highest priority among en_cola only


# ------------------------------------------------- estación 2: operabilidad
def test_operability_rejects_cross_sectional_stocks():
    v = triage_operability.triage_operability(
        {"titulo": "The cross-section of stock returns", "abstract": "decile portfolios of individual stocks"})
    assert v.decision == "reject" and "cross-sectional" in v.razon


def test_operability_rejects_by_declared_universe():
    v = triage_operability.triage_operability(
        {"titulo": "A momentum trading rule", "abstract": "signal", "n_instrumentos": 500})
    assert v.decision == "reject" and "500" in v.razon


def test_operability_rejects_options_but_intraday_now_competes():
    # opciones: sigue siendo un rechazo de operabilidad (dato fuera de alcance)
    assert triage_operability.triage_operability(
        {"titulo": "Variance risk premium", "abstract": "implied volatility and options"}).decision == "reject"
    # CORRECCIÓN de este change: la microestructura intradía ya NO se rechaza por omisión;
    # con datos dentro de presupuesto, COMPITE (cae en el suelo de costos intradía).
    assert triage_operability.triage_operability(
        {"titulo": "Order book imbalance", "abstract": "an order flow trading rule",
         "costo_datos_usd_mes": 0.0}).decision == "keep"


def test_operability_rejects_no_rule():
    v = triage_operability.triage_operability(
        {"titulo": "A survey of financial markets", "abstract": "we review the literature broadly"})
    assert v.decision == "reject" and "regla" in v.razon


def test_operability_keeps_time_series_trend():
    v = triage_operability.triage_operability(
        {"titulo": "Time-series momentum in futures", "abstract": "a trend following trading rule with monthly rebalancing"})
    assert v.decision == "keep"


# ------------------------------------------------- estación 3: costos
def test_required_gross_matches_cost_floor():
    # CFD a duty 100% = 0.64; futuros = 0.424 (docs/cost_floor.md, futures_case.md).
    assert triage_costs.bruto_requerido(1.0, "cfd") == pytest.approx(0.64, abs=1e-9)
    assert triage_costs.bruto_requerido(1.0, "futures") == pytest.approx(0.424, abs=1e-9)
    # coincide con la función reutilizada de costs_model
    assert triage_costs.bruto_requerido(1.0, "cfd") == pytest.approx(
        costs_model.sharpe_bruto_requerido_duty(1.0), abs=1e-9)


def test_cost_triage_rejects_low_gross_both_vehicles():
    v = triage_costs.triage_costs({"duty_cycle_estimado": 1.0, "bruto_reportado": 0.30})
    assert v.decision == "reject"     # 0.30 < 0.424 (fut) y < 0.64 (cfd)


def test_cost_triage_keeps_when_clears_futures_only():
    v = triage_costs.triage_costs({"duty_cycle_estimado": 1.0, "bruto_reportado": 0.50})
    assert v.decision == "keep" and "futuros" in v.razon   # 0.50 > 0.424 but < 0.64


def test_cost_triage_requires_reading_when_no_gross():
    v = triage_costs.triage_costs({"duty_cycle_estimado": 1.0, "bruto_reportado": None})
    assert v.decision == "requiere_lectura"


def test_cost_triage_needs_duty():
    with pytest.raises(ValueError):
        triage_costs.triage_costs({"bruto_reportado": 0.5})


def test_low_duty_lowers_the_required_gross():
    # el requerido de serie completa baja con el duty (0.24·duty + 0.40)
    assert triage_costs.bruto_requerido(0.2, "cfd") < triage_costs.bruto_requerido(1.0, "cfd")


# ------------------------------------------------- estación 3: INTRADÍA
def test_intraday_required_rises_with_trades_per_day():
    r1 = costs_model.sharpe_bruto_requerido_intraday(1, "ES")
    r5 = costs_model.sharpe_bruto_requerido_intraday(5, "ES")
    assert r5 > r1 > 0.40                     # rotar sube el listón por encima del umbral
    # a ~0 trades/día tiende al umbral (coste de rotación → 0)
    assert costs_model.sharpe_bruto_requerido_intraday(0.0, "ES") == pytest.approx(0.40, abs=1e-9)


def test_intraday_crossover_vs_cfd_floor():
    # a partir de ~1.4 round-trips/día el coste ES supera el 1.96%/año del margen CFD
    x = costs_model.trades_por_dia_break_1p96("ES")
    assert 1.2 < x < 1.6
    # y el coste anual a esa frecuencia iguala 1.96%
    assert costs_model.costo_anual_intraday(x, "ES") == pytest.approx(0.0196, rel=1e-6)


def test_intraday_contracts_differ():
    # CL (notional pequeño) es mucho más caro por round-trip que NQ (notional grande)
    assert costs_model.trades_por_dia_break_1p96("CL") < costs_model.trades_por_dia_break_1p96("NQ")


def test_cost_triage_routes_intraday_by_frequency():
    # frecuencia intradía → usa el suelo por rotación, no el swing por duty
    v = triage_costs.triage_costs(
        {"frecuencia": "tick", "trades_por_dia_estimado": 5, "contrato_ref": "ES",
         "bruto_reportado": 0.60})
    assert v.decision == "reject"             # 0.60 < requerido intradía a 5/día (~1.28)
    assert v.requerido_intraday is not None and v.requerido_intraday > 1.0


def test_cost_triage_intraday_needs_trades():
    with pytest.raises(ValueError):
        triage_costs.triage_costs({"frecuencia": "orderbook", "bruto_reportado": 2.0})


# ------------------------------------------------- estación 2: falsabilidad + datos
def test_operability_rejects_non_falsifiable_ict():
    v = triage_operability.triage_operability(
        {"titulo": "Trading order blocks and fair value gaps", "abstract": "smart money concepts"})
    assert v.decision == "reject" and v.categoria == "falsabilidad"


def test_operability_rejects_over_data_budget():
    v = triage_operability.triage_operability(
        {"titulo": "Volume profile strategy", "abstract": "value area trading rule",
         "costo_datos_usd_mes": 133.0})
    assert v.decision == "reject" and v.categoria == "datos"


def test_operability_lets_microstructure_compete():
    # order flow con datos dentro de presupuesto NO se rechaza por omisión: compite
    v = triage_operability.triage_operability(
        {"titulo": "Order flow imbalance in futures", "abstract": "a trading rule using order flow",
         "costo_datos_usd_mes": 0.0})
    assert v.decision == "keep"


def test_operability_flags_volume_profile_incremental_test():
    v = triage_operability.triage_operability(
        {"titulo": "Volume profile levels", "abstract": "trading rule on VAH VAL POC value area",
         "costo_datos_usd_mes": 0.0})
    assert v.decision == "keep" and v.requiere_test_incremental is True


def test_falsifiability_checked_before_data_budget():
    # ICT con datos gratis: igual se rechaza por falsabilidad (categoría, no coste)
    v = triage_operability.triage_operability(
        {"titulo": "order block strategy", "abstract": "fair value gap", "costo_datos_usd_mes": 0.0})
    assert v.categoria == "falsabilidad"


# ------------------------------------------------- estación 1: parsing (sin red)
_ARXIV_FIXTURE = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2401.09999v2</id>
    <title>Time-Series Momentum   Everywhere</title>
    <summary>We document trend
    across asset classes.</summary>
    <published>2024-01-18T10:00:00Z</published>
  </entry>
</feed>"""

_RSS_FIXTURE = """<?xml version="1.0"?>
<rss version="2.0"><channel>
  <item>
    <title>A New Value Factor</title>
    <description>Some description here.</description>
    <link>https://alphaarchitect.com/2024/01/new-value/</link>
    <pubDate>Mon, 15 Jan 2024 12:00:00 +0000</pubDate>
  </item>
</channel></rss>"""


def test_parse_arxiv_atom():
    cands = discover.parse_arxiv_atom(_ARXIV_FIXTURE)
    assert len(cands) == 1
    c = cands[0]
    assert c["id"] == "arxiv:2401.09999"
    assert c["titulo"] == "Time-Series Momentum Everywhere"   # whitespace collapsed
    assert "trend" in c["abstract"]
    assert c["fecha"] == "2024-01-18"
    assert c["fuente"] == "arxiv" and c["fuente_de_la_idea"] == "pipeline"


def test_parse_rss():
    cands = discover.parse_rss(_RSS_FIXTURE, "alpha_architect")
    assert len(cands) == 1
    c = cands[0]
    assert c["fuente"] == "alpha_architect"
    assert c["titulo"] == "A New Value Factor"
    assert c["url"].startswith("https://alphaarchitect.com")


def test_manual_candidate_ssrn():
    c = discover.manual_candidate("https://papers.ssrn.com/abc", "A Paper")
    assert c["fuente"] == "ssrn" and c["fuente_de_la_idea"] == "humano"


# ------------------------------------------------- backfill = conjunto de validación
def test_backfill_loads_nine(conn):
    n = backfill.load_backfill(conn)
    assert n == 9        # 7 EOD + AMT/volume-profile + ICT/SMC
    assert conn.execute("SELECT COUNT(*) FROM hipotesis").fetchone()[0] == 9


def test_backfill_reproduces_zero_survivors(conn):
    backfill.load_backfill(conn)
    vivas = conn.execute(
        "SELECT COUNT(*) FROM hipotesis WHERE estado IN ('viable','en_cola','pre_registrado')"
    ).fetchone()[0]
    assert vivas == 0     # el veredicto conocido: cero supervivientes


def test_backfill_class_distribution(conn):
    backfill.load_backfill(conn)
    rows = dict(conn.execute(
        "SELECT clase_de_dato, COUNT(*) FROM hipotesis GROUP BY clase_de_dato").fetchall())
    assert rows["precio"] == 5           # las 5 price-based originales
    assert rows["calendario"] == 1       # H003
    assert rows["flujo"] == 3            # COT + volume-profile + ICT


def test_backfill_frequency_distribution(conn):
    backfill.load_backfill(conn)
    rows = dict(conn.execute(
        "SELECT frecuencia, COUNT(*) FROM hipotesis GROUP BY frecuencia").fetchall())
    assert rows["EOD"] == 7
    assert rows["intraday_bar"] == 2


def test_backfill_microstructure_reject_reasons(conn):
    backfill.load_backfill(conn)
    assert db.get(conn, "MP001")["estado"] == "rechazada_por_datos"
    assert db.get(conn, "ICT001")["estado"] == "rechazada_por_falsabilidad"


def test_backfill_original_seven_from_reviewer(conn):
    backfill.load_backfill(conn)
    fuentes = {r[0] for r in conn.execute(
        "SELECT DISTINCT fuente_de_la_idea FROM hipotesis WHERE id NOT IN ('MP001','ICT001')")}
    assert fuentes == {"reviewer"}


def test_backfill_is_idempotent(conn):
    backfill.load_backfill(conn)
    backfill.load_backfill(conn)
    assert conn.execute("SELECT COUNT(*) FROM hipotesis").fetchone()[0] == 9


# ------------------------------------------------- reporte de aprendizaje
def test_learning_report_renders(conn):
    backfill.load_backfill(conn)
    txt = learning_report.report(conn)
    assert "Reporte de aprendizaje" in txt
    assert "precio" in txt
    # calibración: sólo las 3 corridas (H001/H003/H007) tienen esperado+medido+fecha_test
    assert "H001" in txt and "H003" in txt and "H007" in txt
    # H002/H005/H006/COT no entran en calibración (sin fecha_test o sin medido)
    cal = learning_report._calibracion(conn)
    assert {r["id"] for r in cal} == {"H001", "H003", "H007"}


def test_calibration_sign_is_overestimate_on_average(conn):
    backfill.load_backfill(conn)
    cal = learning_report._calibracion(conn)
    sesgo_medio = sum(r["sesgo"] for r in cal) / len(cal)
    assert sesgo_medio > 0    # en promedio sobreestimamos el bruto (dominado por H001)
