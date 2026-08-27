"""triage_operability.py — Estación 2: triaje de operabilidad + datos + falsabilidad.

Con título + abstract (+ campos declarados), rechaza lo que NO podemos o NO debemos
operar. IMPORTANTE (corrección de este change): la microestructura/intradía ya NO se
rechaza por omisión — COMPITE EN IGUALDAD, con su listón de costos correcto (estación 3).
Los rechazos de esta estación son:

  1. FALSABILIDAD (filtro #1, distinción de CATEGORÍA): rechaza lo que no mide un dato
     externo y verificable. ICT/SMC (order blocks, fair value gaps, "liquidez
     institucional") se definen sobre el gráfico mismo → no hay dato que los confirme o
     refute. Se ADMITE order flow / volume profile / VPIN / microestructura clásica
     (Kyle, Glosten-Milgrom): miden algo que existe en un archivo de datos.
  2. DATOS: coste de datos > presupuesto configurable (por defecto 60 USD/mes).
  3. OPERABILIDAD clásica: cross-sectional de acciones (>100 instrumentos), opciones/vol
     implícita, fundamentales point-in-time, o sin regla operativa identificable.

DECISIÓN DE ALCANCE: heurística determinista sobre palabras clave, con interfaz limpia
donde un modelo pequeño puede sustituirla. Extracción con LLM fuera de alcance.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Presupuesto de datos por defecto (USD/mes). Configurable en `apply`.
# 125 USD/mes (≈500k COP, decisión del operador). Admite Norgate futures EOD (~$50), Binance
# (gratis), Deribit opciones cripto (gratis), BIS/FRED/CFTC/LOBSTER (gratis). NO admite:
# opciones de acciones/SPX, Databento ($199/$1750, además BANEADO por ToS), Polygon ($199),
# IQFeed (~$133, frontera). Ver docs/research_pipeline.md y docs/pipeline_stop_condition.md.
DATA_BUDGET_USD = 125.0

# --- FALSABILIDAD: rechazadas por no medir un dato externo (ICT/SMC) ---
# Se casan con LÍMITE DE PALABRA (\b…\b): los acrónimos cortos ("ict", "smc", "fvg") como
# SUBCADENA daban falsos positivos — "ict " casaba dentro de "predict ", "explicit ",
# "restrict " (bug hallado en la primera corrida live, pipeline-first-live-run: dos papers
# de vol-risk-premium y rebalanceo rechazados por error). Ver triage con `_hits_word`.
_NON_FALSIFIABLE = (
    "order block", "orderblock", "fair value gap", "fvg", "smart money concept",
    "smart money", "liquidity grab", "liquidity sweep", "liquidity pool",
    "inner circle trader", "ict", "smc", "judas swing", "optimal trade entry",
    "breaker block", "mitigation block", "institutional liquidity",
)
# --- señales de cross-sectional de acciones (universo enorme, no operable en prop) ---
_CROSS_SECTIONAL = (
    "cross-section", "cross section", "cross-sectional", "the cross section",
    "stock returns", "individual stocks", "equity anomal", "firm characteristic",
    "crsp", "compustat", "s&p 500 constituent", "russell 3000", "universe of stocks",
    "portfolio sort", "decile portfolio", "long-short equity", "fama-macbeth",
)
_NEEDS_OPTIONS = (
    "option", "implied volatility", "vix", "variance risk premium", "straddle",
    "put-call", "iv surface", "volatility surface", "skew",
)
_NEEDS_FUNDAMENTALS = (
    "earnings announcement", "balance sheet", "accrual", "book-to-market",
    "fundamental", "analyst forecast", "sec filing", "10-k", "10-q",
    "dividend yield anomal",
)
# --- señales POSITIVAS de una regla operativa identificable (incluye microestructura) ---
_HAS_RULE = (
    "time-series momentum", "time series momentum", "trend following", "trend-following",
    "carry", "moving average", "breakout", "mean reversion", "mean-reversion",
    "seasonal", "risk premium", "momentum", "signal", "trading rule", "long-short",
    "go long", "go short", "rebalanc",
    # microestructura ADMITIDA
    "order flow", "order-flow", "volume profile", "vpin", "order imbalance",
    "order-flow imbalance", "price impact", "trade classification", "market microstructure",
    "limit order book", "footprint", "value area",
)
# --- volume profile: requiere test INCREMENTAL vs niveles simples ---
_VOLUME_PROFILE = (
    "volume profile", "value area", "vah", "val", "poc", "point of control",
    "volume-at-price", "volume at price", "market profile",
)


@dataclass(frozen=True)
class OperabilityVerdict:
    decision: str                 # keep | reject
    razon: str
    categoria: str | None = None  # falsabilidad | datos | operabilidad (en reject)
    requiere_test_incremental: bool = False


def _hits(text: str, needles) -> str | None:
    for n in needles:
        if n in text:
            return n
    return None


def _hits_word(text: str, needles) -> str | None:
    """Como `_hits` pero con LÍMITE DE PALABRA: evita que un acrónimo corto ('ict', 'smc',
    'fvg') case como subcadena dentro de otra palabra ('predict', 'explicit'). Multi-palabra
    ('order block') también casa correctamente con \\b."""
    for n in needles:
        if re.search(r"\b" + re.escape(n) + r"\b", text):
            return n
    return None


def triage_operability(candidate: dict, *, budget_usd: float = DATA_BUDGET_USD) -> OperabilityVerdict:
    """keep/reject + razón + categoría, a partir de título + abstract + campos declarados."""
    text = f"{candidate.get('titulo', '')} {candidate.get('abstract', '')}".lower()
    text = re.sub(r"\s+", " ", text)

    # 1. FALSABILIDAD primero (distinción de categoría, no de estilo). Límite de palabra:
    # los acrónimos ICT/SMC/FVG no deben casar dentro de "predict"/"explicit"/etc.
    hit = _hits_word(text, _NON_FALSIFIABLE)
    if hit:
        return OperabilityVerdict("reject",
            f"no falsable: '{hit}' se define sobre el gráfico, sin dato externo que lo "
            f"confirme o refute (filtro #1)", categoria="falsabilidad")

    # 2. DATOS: presupuesto.
    costo = candidate.get("costo_datos_usd_mes")
    if isinstance(costo, (int, float)) and costo > budget_usd:
        return OperabilityVerdict("reject",
            f"coste de datos {costo:.0f} USD/mes > presupuesto {budget_usd:.0f} USD/mes",
            categoria="datos")

    # 3. OPERABILIDAD clásica.
    n = candidate.get("n_instrumentos")
    if isinstance(n, (int, float)) and n > 100:
        return OperabilityVerdict("reject", f"universo declarado {int(n)} > 100 (cross-sectional)",
                                  categoria="operabilidad")
    hit = _hits(text, _CROSS_SECTIONAL)
    if hit:
        return OperabilityVerdict("reject", f"cross-sectional de acciones (señal: '{hit}')",
                                  categoria="operabilidad")
    hit = _hits(text, _NEEDS_OPTIONS)
    if hit:
        return OperabilityVerdict("reject", f"requiere datos de opciones/vol implícita (señal: '{hit}')",
                                  categoria="operabilidad")
    hit = _hits(text, _NEEDS_FUNDAMENTALS)
    if hit:
        return OperabilityVerdict("reject", f"requiere fundamentales point-in-time (señal: '{hit}')",
                                  categoria="operabilidad")
    if not text.strip():
        return OperabilityVerdict("reject", "sin título ni abstract: no hay regla identificable",
                                  categoria="operabilidad")
    if _hits(text, _HAS_RULE) is None:
        return OperabilityVerdict("reject", "sin regla operativa identificable en el abstract",
                                  categoria="operabilidad")

    # keep — con la marca de test incremental para volume profile.
    vp = _hits(text, _VOLUME_PROFILE) is not None
    razon = "series temporales/microestructura, datos dentro de presupuesto, regla identificable"
    if vp:
        razon += " · volume profile → requiere test INCREMENTAL vs niveles simples"
    return OperabilityVerdict("keep", razon, requiere_test_incremental=vp)


def apply(conn, hyp_id: str, candidate: dict | None = None, *,
          budget_usd: float = DATA_BUDGET_USD) -> OperabilityVerdict:
    """Correr el triaje sobre una fila de la DB y persistir el resultado."""
    from src.pipeline import db

    row = candidate or db.get(conn, hyp_id)
    if row is None:
        raise KeyError(hyp_id)
    verdict = triage_operability(row, budget_usd=budget_usd)
    update = {
        "id": hyp_id,
        "triage_operabilidad": verdict.decision,
        "triage_operabilidad_razon": verdict.razon,
        "operable_en_prop": 1 if verdict.decision == "keep" else 0,
        "requiere_test_incremental": 1 if verdict.requiere_test_incremental else 0,
    }
    if verdict.decision == "reject":
        update["estado"] = {
            "falsabilidad": "rechazada_por_falsabilidad",
            "datos": "rechazada_por_datos",
            "operabilidad": "rechazada_operabilidad",
        }.get(verdict.categoria, "rechazada_operabilidad")
    db.upsert(conn, update)
    return verdict
