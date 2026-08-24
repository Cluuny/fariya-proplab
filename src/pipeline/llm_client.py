"""llm_client.py — el seam de LLM para las estaciones 4-5, listo para automatizar.

NO está conectado a ninguna API en este change (validación manual asistida primero). Aquí
vive la plomería que hará falta para automatizar:
  - firma clara: un `llm_call(pdf_text) -> dict` inyectable
  - credencial por VARIABLE DE ENTORNO (nunca en el repo)
  - structured output obligatorio: la ficha valida contra el esquema o se RECHAZA
  - log de cada llamada: prompt, respuesta cruda, tokens
  - reintento con backoff, fallo VISIBLE si la respuesta no valida
La lógica de reintento/validación/log es testeable con un `llm_call` falso, sin API real.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

from src.pipeline import extract

LLM_API_KEY_ENV = "PIPELINE_LLM_API_KEY"     # p.ej. exportar la key aquí; NUNCA en el repo
LLM_MODEL_ENV = "PIPELINE_LLM_MODEL"
LOG_DIR = Path("results/pipeline/llm_logs")   # gitignored (results/*)


class LLMNotConfigured(RuntimeError):
    """No hay credencial/SDK para llamar al modelo. Se explica cómo configurarlo."""


class ExtractionFailed(RuntimeError):
    """La respuesta del modelo no validó tras los reintentos (fallo visible)."""


def _log_call(paper_id: str, attempt: int, prompt: str, raw: str, tokens: dict | None) -> None:
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        rec = {"paper_id": paper_id, "attempt": attempt, "prompt_chars": len(prompt),
               "raw": raw, "tokens": tokens}
        with open(LOG_DIR / f"{paper_id}.jsonl", "a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception as ex:  # noqa: BLE001 — el log no debe tumbar la extracción
        print(f"[llm_client] no pude loguear: {ex}")


def extract_with_retry(llm_call, paper_id: str, pdf_text: str, *,
                       max_retries: int = 3, backoff_s: float = 2.0) -> extract.ExtractionResult:
    """Llama a `llm_call(pdf_text) -> dict`, valida con `extract.validate_extraction`, y
    reintenta con backoff si la respuesta no valida o si `llm_call` levanta. Devuelve el
    ExtractionResult ACEPTADO; si nunca valida, levanta ExtractionFailed (fallo visible).

    `llm_call` debe devolver un dict (structured output). El log guarda prompt/respuesta/tokens.
    """
    last_reason = None
    for attempt in range(1, max_retries + 1):
        try:
            out = llm_call(pdf_text)
            raw = out if isinstance(out, str) else json.dumps(out, ensure_ascii=False)
            tokens = out.get("_tokens") if isinstance(out, dict) else None
            _log_call(paper_id, attempt, prompt="<pdf_text>", raw=raw, tokens=tokens)
            data = json.loads(out) if isinstance(out, str) else out
            res = extract.validate_extraction(data)
            if res.accepted:
                return res
            last_reason = res.reject_reason
        except Exception as ex:  # noqa: BLE001
            last_reason = f"{type(ex).__name__}: {ex}"
        if attempt < max_retries:
            time.sleep(backoff_s * attempt)   # backoff lineal
    raise ExtractionFailed(f"'{paper_id}' no validó tras {max_retries} intentos: {last_reason}")


def make_api_extractor(*, model: str | None = None, api_key: str | None = None):
    """SEAM: construye un `llm_call(pdf_text)->dict` que llama a la API con structured output.

    NO se conecta en este change. Requiere `PIPELINE_LLM_API_KEY` (o `api_key=`) y el SDK del
    proveedor instalado. Sin credencial → LLMNotConfigured con instrucciones (no hay fallback
    silencioso). El prompt DEBE exigir: cada campo numérico con su `cita_<campo>`; y un
    `falsador` escribible (si no, la validación lo rechaza aguas abajo)."""
    key = api_key or os.environ.get(LLM_API_KEY_ENV)
    if not key:
        raise LLMNotConfigured(
            f"falta credencial: exporta {LLM_API_KEY_ENV} (nunca en el repo). "
            f"Ver data/papers/README.md / docs/extraction_validation.md para activarlo.")
    model = model or os.environ.get(LLM_MODEL_ENV, "claude-haiku-4-5-20251001")

    def _call(pdf_text: str) -> dict:  # pragma: no cover - requiere API real
        raise LLMNotConfigured(
            "adaptador de API no cableado en este change (pipeline-llm-live es validación "
            "manual). Implementar aquí la llamada con structured output usando el SDK del "
            f"proveedor y el modelo {model!r}; devolver dict con campos + cita_<campo> + _tokens.")
    return _call
