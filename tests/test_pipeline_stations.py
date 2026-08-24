"""Tests de las estaciones 4-7 del pipeline (extracción, adversaria, stub, compuerta)."""

from __future__ import annotations

import pytest

from src.pipeline import adversarial, db, extract, human_gate, stub_gen


# ---------------------------------------------- Estación 4: extracción / validación
def _good_ficha(**over):
    f = {"titulo": "T", "familia": "trend", "mecanismo": "conductual",
         "hipotesis": "el signo predice", "regla_entrada": "long si >0",
         "falsador": "si Sharpe neto < 0.2, muere",
         "bruto_reportado": 1.2, "cita_bruto": "Tabla 2"}
    f.update(over)
    return f


def test_extraction_accepts_well_formed():
    r = extract.validate_extraction(_good_ficha())
    assert r.accepted and not r.dropped_fields
    assert r.ficha["bruto_reportado"] == 1.2


def test_extraction_drops_numeric_without_citation():
    r = extract.validate_extraction(_good_ficha(cita_bruto=None))
    assert r.accepted                              # sigue siendo hipótesis válida
    assert "bruto_reportado" in r.dropped_fields
    assert r.ficha["bruto_reportado"] is None      # a null por falta de cita


def test_extraction_rejects_without_falsador():
    r = extract.validate_extraction(_good_ficha(falsador=""))
    assert not r.accepted and "FALSADOR" in r.reject_reason


def test_extraction_rejects_missing_required_fields():
    r = extract.validate_extraction(_good_ficha(regla_entrada=""))
    assert not r.accepted and "mínimos" in r.reject_reason


def test_extract_from_pdf_seam_requires_llm():
    with pytest.raises(NotImplementedError):
        extract.extract_from_pdf("paper.pdf")


# ---------------------------------------------- Estación 5: revisión adversaria
def _all_pass():
    return {k: True for k, _q, _c in adversarial.ATTACK_QUESTIONS}


def test_adversarial_keeps_when_all_pass():
    assert adversarial.evaluate(_all_pass()).veredicto == "keep"


def test_adversarial_rejects_on_critical_failure():
    f = _all_pass(); f["contemporaneo_vs_predictivo"] = False   # eje crítico (lección OFI/H003)
    r = adversarial.evaluate(f)
    assert r.veredicto == "reject" and "contemporaneo_vs_predictivo" in r.failed_axes


def test_adversarial_non_critical_failure_keeps():
    f = _all_pass(); f["n_variantes"] = False                   # no crítico
    assert adversarial.evaluate(f).veredicto == "keep"


def test_adversarial_missing_axis_counts_against():
    f = _all_pass(); del f["benchmark_cero"]                    # ausente → no superado
    assert adversarial.evaluate(f).veredicto == "reject"


# ---------------------------------------------- Estación 6: generación de stub
def test_stub_generation_has_fixed_contract():
    code = stub_gen.generate_stub(_good_ficha(id="H099", titulo="Test",
                                              regla_salida="mensual", clase_de_dato="precio"))
    assert "def signal_h099(prices: pd.DataFrame) -> pd.DataFrame:" in code
    assert "NotImplementedError" in code           # no inventa la señal
    assert "FALSADOR" in code                       # el falsador viaja al stub


# ---------------------------------------------- Estación 7: compuerta humana
def test_human_gate_surfaces_and_approves():
    c = db.connect(":memory:"); db.init_db(c)
    db.upsert(c, {"id": "P1", "titulo": "cand", "estado": "en_cola", "score_prioridad": 0.9,
                  "adversarial_veredicto": "keep"})
    db.upsert(c, {"id": "P2", "titulo": "rej", "estado": "en_cola",
                  "adversarial_veredicto": "reject"})
    cands = human_gate.candidates_for_review(c)
    assert [x["id"] for x in cands] == ["P1"]       # el rechazado por adversaria no aparece
    human_gate.approve(c, "P1")
    assert db.get(c, "P1")["estado"] == "pre_registrado"
    c.close()
