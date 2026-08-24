"""extract.py — Estación 4: extracción del PDF completo → ficha, con validación de esquema.

El LLM lee el PDF completo y emite structured output. Este módulo IMPONE las dos reglas
anti-alucinación (la parte testeable y crítica; la llamada al LLM es el `seam`):

  (a) cada campo NUMÉRICO exige CITA DE UBICACIÓN (sección o tabla). Sin cita, el campo va
      a null. Los LLM inventan Sharpes con facilidad.
  (b) sin FALSADOR escribible, el registro se RECHAZA por validación de esquema. Impide
      acumular "ideas interesantes" sin criterio de muerte.

DECISIÓN DE ALCANCE: la extracción con LLM (PDF→dict) es el `seam` — se invoca con el Agent
tool / un modelo pequeño en producción. Aquí se implementa y testea la VALIDACIÓN, que es lo
que evita que la basura entre a la cola.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Campos numéricos → su campo de cita de ubicación (regla a).
NUMERIC_FIELDS_REQUIRING_CITATION = {"bruto_reportado": "cita_bruto"}
# Campos mínimos para que una ficha sea una HIPÓTESIS (no contenido).
REQUIRED_FIELDS = ("titulo", "familia", "mecanismo", "hipotesis", "regla_entrada", "falsador")


@dataclass
class ExtractionResult:
    ficha: dict
    accepted: bool
    dropped_fields: list[str] = field(default_factory=list)   # numéricos sin cita → null
    reject_reason: str | None = None


def validate_extraction(raw: dict) -> ExtractionResult:
    """Aplica las dos reglas anti-alucinación a un dict extraído del PDF.

    - Regla (a): un campo numérico sin su `cita_<campo>` (str no vacío) se pone a null y se
      registra en `dropped_fields`.
    - Regla (b): sin `falsador` escribible (str no vacío) → rechazo por esquema.
    - Además exige los campos mínimos de una hipótesis (REQUIRED_FIELDS).
    """
    ficha = dict(raw)
    dropped = []

    # (a) cada numérico exige cita
    for fld, cita_fld in NUMERIC_FIELDS_REQUIRING_CITATION.items():
        if ficha.get(fld) is not None:
            cita = ficha.get(cita_fld)
            if not (isinstance(cita, str) and cita.strip()):
                ficha[fld] = None
                dropped.append(fld)

    # (b) sin falsador escribible → rechazo
    fals = ficha.get("falsador")
    if not (isinstance(fals, str) and fals.strip()):
        return ExtractionResult(ficha=ficha, accepted=False, dropped_fields=dropped,
                                reject_reason="sin FALSADOR escribible → rechazado por esquema "
                                              "(no se acumulan 'ideas interesantes')")

    # campos mínimos de una hipótesis
    missing = [f for f in REQUIRED_FIELDS
               if not (isinstance(ficha.get(f), str) and ficha[f].strip())]
    if missing:
        return ExtractionResult(ficha=ficha, accepted=False, dropped_fields=dropped,
                                reject_reason=f"faltan campos mínimos de hipótesis: {missing}")

    return ExtractionResult(ficha=ficha, accepted=True, dropped_fields=dropped)


def extract_from_pdf(path, *, llm=None) -> dict:
    """SEAM: extraer una ficha estructurada de un PDF completo con un LLM (structured output
    obligatorio). En producción se inyecta `llm` (Agent tool / modelo pequeño) que devuelve el
    dict con los campos y sus `cita_<campo>`. Sin `llm` inyectado, se documenta el contrato y
    se levanta NotImplementedError (no se inventan datos)."""
    if llm is None:
        raise NotImplementedError(
            "extracción LLM no inyectada. Contrato: llm(pdf_text) → dict con campos de ficha "
            "+ cita_<campo> por cada numérico. La validación (validate_extraction) es lo que "
            "impone las reglas anti-alucinación.")
    return llm(path)
