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


def test_operability_rejects_options_and_intraday():
    assert triage_operability.triage_operability(
        {"titulo": "Variance risk premium", "abstract": "implied volatility and options"}).decision == "reject"
    assert triage_operability.triage_operability(
        {"titulo": "Order book imbalance", "abstract": "intraday high-frequency signal"}).decision == "reject"


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
def test_backfill_loads_seven(conn):
    n = backfill.load_backfill(conn)
    assert n == 7
    assert conn.execute("SELECT COUNT(*) FROM hipotesis").fetchone()[0] == 7


def test_backfill_reproduces_zero_survivors(conn):
    backfill.load_backfill(conn)
    vivas = conn.execute(
        "SELECT COUNT(*) FROM hipotesis WHERE estado IN ('viable','en_cola','pre_registrado')"
    ).fetchone()[0]
    assert vivas == 0     # el veredicto conocido: cero supervivientes


def test_backfill_class_distribution_is_5_precio(conn):
    backfill.load_backfill(conn)
    rows = dict(conn.execute(
        "SELECT clase_de_dato, COUNT(*) FROM hipotesis GROUP BY clase_de_dato").fetchall())
    assert rows["precio"] == 5
    assert rows["calendario"] == 1
    assert rows["flujo"] == 1


def test_backfill_all_from_reviewer(conn):
    backfill.load_backfill(conn)
    fuentes = {r[0] for r in conn.execute("SELECT DISTINCT fuente_de_la_idea FROM hipotesis")}
    assert fuentes == {"reviewer"}


def test_backfill_is_idempotent(conn):
    backfill.load_backfill(conn)
    backfill.load_backfill(conn)
    assert conn.execute("SELECT COUNT(*) FROM hipotesis").fetchone()[0] == 7


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
