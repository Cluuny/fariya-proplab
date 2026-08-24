"""triage_operability.py — Estación 2: triaje de operabilidad.

Con título + abstract, rechazar lo que NO podemos operar en una cuenta de fondeo con
nuestro panel EOD spot/CFD (o futuros). Rechaza si:
  - cross-sectional de acciones (universo > 100 instrumentos)
  - requiere datos que no tenemos (opciones, intradía con volumen real, fundamentales
    point-in-time de empresas)
  - intradía
  - sin regla operativa identificable

DECISIÓN DE ALCANCE: este esqueleto implementa el triaje como HEURÍSTICA determinista
sobre palabras clave del título+abstract, con una interfaz limpia (`triage_operability`)
donde un modelo pequeño puede sustituir la heurística más adelante. La extracción con LLM
está explícitamente fuera de alcance de este change (sólo si el mes de futuros da luz
verde). La heurística es conservadora: ante la duda, `keep` (que caiga en el triaje de
costos, más barato y discriminante).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Señales de cross-sectional de acciones (universo enorme, no operable en prop).
_CROSS_SECTIONAL = (
    "cross-section", "cross section", "cross-sectional", "the cross section",
    "stock returns", "individual stocks", "equity anomal", "firm characteristic",
    "crsp", "compustat", "s&p 500 constituent", "russell 3000", "universe of stocks",
    "portfolio sort", "decile portfolio", "long-short equity", "fama-macbeth",
)
# Señales de datos que NO tenemos.
_NEEDS_OPTIONS = (
    "option", "implied volatility", "vix", "variance risk premium", "straddle",
    "put-call", "iv surface", "volatility surface", "skew",
)
_NEEDS_FUNDAMENTALS = (
    "earnings announcement", "balance sheet", "accrual", "book-to-market",
    "fundamental", "analyst forecast", "sec filing", "10-k", "10-q",
    "dividend yield anomal",
)
_INTRADAY = (
    "intraday", "high-frequency", "high frequency", "microstructure",
    "order book", "limit order", "tick data", "millisecond", "minute-bar",
    "minute bar", "order flow imbalance",
)
# Señales POSITIVAS de una regla operativa identificable.
_HAS_RULE = (
    "time-series momentum", "time series momentum", "trend following", "trend-following",
    "carry", "moving average", "breakout", "mean reversion", "mean-reversion",
    "seasonal", "risk premium", "momentum", "signal", "trading rule", "long-short",
    "go long", "go short", "rebalanc",
)


@dataclass(frozen=True)
class OperabilityVerdict:
    decision: str   # keep | reject
    razon: str


def _hits(text: str, needles) -> str | None:
    for n in needles:
        if n in text:
            return n
    return None


def triage_operability(candidate: dict) -> OperabilityVerdict:
    """keep/reject + razón en una línea, a partir de título + abstract.

    Un `n_instrumentos` declarado > 100 es un rechazo directo (cross-sectional) aunque el
    texto no lo delate.
    """
    text = f"{candidate.get('titulo', '')} {candidate.get('abstract', '')}".lower()
    text = re.sub(r"\s+", " ", text)

    n = candidate.get("n_instrumentos")
    if isinstance(n, (int, float)) and n > 100:
        return OperabilityVerdict("reject", f"universo declarado {int(n)} > 100 (cross-sectional)")

    hit = _hits(text, _CROSS_SECTIONAL)
    if hit:
        return OperabilityVerdict("reject", f"cross-sectional de acciones (señal: '{hit}')")
    hit = _hits(text, _INTRADAY)
    if hit:
        return OperabilityVerdict("reject", f"intradía / alta frecuencia (señal: '{hit}')")
    hit = _hits(text, _NEEDS_OPTIONS)
    if hit:
        return OperabilityVerdict("reject", f"requiere datos de opciones/vol implícita (señal: '{hit}')")
    hit = _hits(text, _NEEDS_FUNDAMENTALS)
    if hit:
        return OperabilityVerdict("reject", f"requiere fundamentales point-in-time (señal: '{hit}')")

    if not text.strip():
        return OperabilityVerdict("reject", "sin título ni abstract: no hay regla identificable")
    if _hits(text, _HAS_RULE) is None:
        return OperabilityVerdict("reject", "sin regla operativa identificable en el abstract")

    return OperabilityVerdict("keep", "series temporales, datos que tenemos, regla identificable")


def apply(conn, hyp_id: str, candidate: dict | None = None) -> OperabilityVerdict:
    """Correr el triaje sobre una fila de la DB y persistir el resultado."""
    from src.pipeline import db

    row = candidate or db.get(conn, hyp_id)
    if row is None:
        raise KeyError(hyp_id)
    verdict = triage_operability(row)
    update = {
        "id": hyp_id,
        "triage_operabilidad": verdict.decision,
        "triage_operabilidad_razon": verdict.razon,
        "operable_en_prop": 1 if verdict.decision == "keep" else 0,
    }
    if verdict.decision == "reject":
        update["estado"] = "rechazada_operabilidad"
    db.upsert(conn, update)
    return verdict
