"""Tests del seam de LLM (llm_client): reintento, validación, credencial, y un test de
integración marcado skip-si-no-hay-credencial."""

from __future__ import annotations

import os

import pytest

from src.pipeline import extract, llm_client


def _valid_ficha():
    return {"titulo": "T", "familia": "trend", "mecanismo": "m",
            "hipotesis": "h", "regla_entrada": "long si >0",
            "falsador": "si Sharpe neto < 0.2, muere",
            "bruto_reportado": 1.0, "cita_bruto": "Tabla 2"}


def test_retry_returns_on_first_valid(tmp_path, monkeypatch):
    monkeypatch.setattr(llm_client, "LOG_DIR", tmp_path)
    res = llm_client.extract_with_retry(lambda _t: _valid_ficha(), "p1", "texto", backoff_s=0)
    assert res.accepted and res.ficha["titulo"] == "T"


def test_retry_recovers_after_invalid(tmp_path, monkeypatch):
    monkeypatch.setattr(llm_client, "LOG_DIR", tmp_path)
    calls = {"n": 0}

    def flaky(_t):
        calls["n"] += 1
        return {"titulo": "x"} if calls["n"] == 1 else _valid_ficha()  # 1º sin falsador → inválida

    res = llm_client.extract_with_retry(flaky, "p2", "texto", backoff_s=0)
    assert res.accepted and calls["n"] == 2


def test_retry_fails_visibly_after_max(tmp_path, monkeypatch):
    monkeypatch.setattr(llm_client, "LOG_DIR", tmp_path)
    with pytest.raises(llm_client.ExtractionFailed):
        llm_client.extract_with_retry(lambda _t: {"titulo": "no falsador"}, "p3", "t",
                                      max_retries=2, backoff_s=0)


def test_retry_logs_each_call(tmp_path, monkeypatch):
    monkeypatch.setattr(llm_client, "LOG_DIR", tmp_path)
    llm_client.extract_with_retry(lambda _t: _valid_ficha(), "p4", "texto", backoff_s=0)
    log = tmp_path / "p4.jsonl"
    assert log.exists() and log.read_text().strip()


def test_make_api_extractor_requires_credential(monkeypatch):
    monkeypatch.delenv(llm_client.LLM_API_KEY_ENV, raising=False)
    with pytest.raises(llm_client.LLMNotConfigured):
        llm_client.make_api_extractor()


def test_api_adapter_not_wired_yet(monkeypatch):
    # con credencial presente, el adaptador se construye pero NO está cableado (este change)
    monkeypatch.setenv(llm_client.LLM_API_KEY_ENV, "dummy")
    call = llm_client.make_api_extractor()
    with pytest.raises(llm_client.LLMNotConfigured):
        call("texto")


@pytest.mark.skipif(not os.environ.get(llm_client.LLM_API_KEY_ENV),
                    reason="sin credencial LLM: test de integración omitido")
def test_integration_real_extraction():
    """Test de integración: sólo corre si hay PIPELINE_LLM_API_KEY. Cuando el adaptador esté
    cableado (change siguiente), extrae un paper real y valida la ficha."""
    from src.pipeline import papers
    pdf = papers.resolve_paper("contkukanov2011_ofi")
    call = llm_client.make_api_extractor()
    res = llm_client.extract_with_retry(call, "contkukanov2011_ofi", pdf.read_text(errors="ignore"))
    assert res.accepted
