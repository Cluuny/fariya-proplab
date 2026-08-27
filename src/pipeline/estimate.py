"""estimate.py — Estación 2.5: estimación DETERMINISTA de los campos que E3 necesita.

E3 (triaje de costes) es aritmética pura, pero requiere campos que hasta ahora nadie
llenaba desde el abstract (`frecuencia`, `duty_cycle_estimado`, `bruto_reportado`, …). El
runner los dejaba en None y SALTABA el triaje de costes. Este módulo convierte esa parte
a HEURÍSTICA DETERMINISTA — reglas de palabras clave + una extracción por regex del Sharpe
si está EN EL ABSTRACT — para que E1-E3 corran en batch, sin sesión ni LLM.

Principio (decisión del operador, change pipeline-first-live-run): «El triaje por abstract
no necesita un modelo: palabras clave de universo, frecuencia, tipo de dato, y el cálculo
del requerido son reglas.» La lectura del PAPER completo (E4) sí es una tarea de juicio y va
en sesión; esto es sólo el cribado barato previo.

REGLA ANTI-ALUCINACIÓN aquí también: `bruto_reportado` sólo se llena si un número plausible
aparece JUNTO a la palabra "Sharpe" en el abstract; su cita es `"abstract"` (ubicación real,
texto no figura). Si no aparece → None → E3 marca `requiere_lectura` (no se descarta). No se
inventa un Sharpe: la ausencia es un estado válido, no un cero.
"""

from __future__ import annotations

import re

# --- FRECUENCIA: señales, de la más específica (order book) a la menos (EOD por defecto) ---
_ORDERBOOK = (
    "order book", "order-book", "limit order book", "lob ", "order flow", "order-flow",
    "order imbalance", "order-flow imbalance", "best bid", "best ask", "quote", "depth of book",
    "microsecond", "nanosecond", "vpin",
)
_TICK = ("tick data", "tick-by-tick", "trade-by-trade", "tick level", "tick-level")
_INTRADAY = (
    "intraday", "intra-day", "high-frequency", "high frequency", "minute bar", "1-minute",
    "5-minute", "one-minute", "five-minute", "minute-level", "hourly", "seconds", "second-by-second",
)
# --- DUTY bajo: estrategias de calendario/evento (fuera del mercado la mayor parte del tiempo) ---
_LOW_DUTY = (
    "turn-of-the-month", "turn of the month", "turn-of-month", "seasonal", "seasonality",
    "day-of-the-week", "day of the week", "day-of-week", "holiday", "halloween", "january effect",
    "monday effect", "weekend effect", "around earnings", "earnings announcement", "event study",
    "announcement", "fomc", "expiration", "expiry", "calendar anomaly", "calendar effect",
    "pre-holiday", "intramonth", "monthly effect",
)
_LOW_DUTY_VALUE = 0.15   # ~4 de ~21 días (H003 real 0.19); conservador y documentado

# --- CLASE DE DATO por palabras clave (para el registro de aprendizaje / prioridad) ---
_CLASE_RULES = (
    ("flujo",                 ("order flow", "order-flow", "order book", "order imbalance", "volume profile",
                               "value area", "vpin", "microstructure", "trade imbalance", "footprint",
                               "cot ", "positioning", "commitment of traders")),
    ("volatilidad_implicita", ("implied volatility", "option", "variance risk premium", "vix", "straddle", "iv surface")),
    ("calendario",            ("turn-of-the-month", "turn of the month", "seasonal", "day-of-the-week",
                               "calendar", "holiday", "january effect")),
    ("macro",                 ("macroeconomic", "interest rate", "inflation", "monetary policy", "central bank",
                               "yield curve", "term structure", "gdp", "unemployment")),
    ("fundamental",           ("earnings", "book-to-market", "accrual", "balance sheet", "fundamental",
                               "analyst forecast", "dividend")),
    ("estructura_temporal",   ("term structure", "futures curve", "roll yield", "contango", "backwardation")),
)

# --- TURNOVER (rotaciones/año, orientativo; no decide en EOD) ---
_TURNOVER_RULES = (
    (252.0, ("daily rebalanc", "rebalanced daily", "daily signal")),
    (52.0,  ("weekly rebalanc", "weekly signal", "weekly")),
    (12.0,  ("monthly rebalanc", "monthly signal", "monthly")),
    (4.0,   ("quarterly",)),
    (1.0,   ("annual rebalanc", "yearly")),
)

# rango plausible de un Sharpe reportado (descarta años "2019", porcentajes, t-stats enormes)
_SHARPE_MIN, _SHARPE_MAX = 0.05, 10.0
# "Sharpe" seguido, dentro de una ventana corta, de un número (con conectores opcionales)
_SHARPE_RE = re.compile(
    r"sharpe(?:\s+ratio)?(?:\s*\([^)]*\))?\s*"
    r"(?:ratio\s*)?(?:of|=|:|is|are|around|near|approximately|about|up to|exceeding|above|reaches?|reaching|equal to)?\s*"
    r"(\d+(?:\.\d+)?)",
    re.IGNORECASE,
)


def _text(candidate: dict) -> str:
    t = f"{candidate.get('titulo', '')} {candidate.get('abstract', '')}".lower()
    return re.sub(r"\s+", " ", t)


def _hit(text: str, needles) -> bool:
    return any(n in text for n in needles)


def estimate_frecuencia(text: str) -> str:
    if _hit(text, _ORDERBOOK):
        return "orderbook"
    if _hit(text, _TICK):
        return "tick"
    if _hit(text, _INTRADAY):
        return "intraday_bar"
    return "EOD"


def estimate_duty(text: str) -> float:
    """Duty EOD: 1.0 (continuo, el caso común de trend/carry/reversión time-series) salvo que
    el abstract señale una estrategia de calendario/evento → 0.15. Estimación grosera y
    documentada; el duty REAL se mide al correr (como en H008: 0.20 a priori → 0.31 medido)."""
    return _LOW_DUTY_VALUE if _hit(text, _LOW_DUTY) else 1.0


def estimate_clase(text: str) -> str:
    for clase, needles in _CLASE_RULES:
        if _hit(text, needles):
            return clase
    return "precio"


def estimate_turnover(text: str, frecuencia: str) -> float:
    for val, needles in _TURNOVER_RULES:
        if _hit(text, needles):
            return val
    # por defecto según frecuencia
    return {"EOD": 12.0, "intraday_bar": 252.0 * 10, "tick": 252.0 * 50, "orderbook": 252.0 * 50}[frecuencia]


def estimate_trades_por_dia(text: str, frecuencia: str) -> float:
    if frecuencia == "EOD":
        return 0.0
    # "N trades per day" explícito
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:round[- ]?trips?|trades?)\s*(?:per|/|a)\s*day", text)
    if m:
        return float(m.group(1))
    if _hit(text, ("high-frequency", "high frequency")):
        return 100.0
    return {"intraday_bar": 10.0, "tick": 50.0, "orderbook": 50.0}[frecuencia]


def estimate_contrato(text: str) -> str:
    """Contrato de referencia para el suelo intradía (ES/NQ/CL/GC). Cripto/FX no tienen
    contrato CME → se usa ES como proxy y se anota; el suelo cripto real es otro (ver OFI)."""
    if _hit(text, ("nasdaq", "nq ", "tech stock")):
        return "NQ"
    if _hit(text, ("crude", "oil", "wti", "energy")):
        return "CL"
    if _hit(text, ("gold", "xau", "precious metal")):
        return "GC"
    return "ES"


def extract_bruto_reportado(candidate: dict) -> tuple[float | None, str | None]:
    """Extrae el Sharpe reportado SÓLO si aparece en el abstract junto a "Sharpe".

    Devuelve (valor, cita). Regla anti-alucinación: sin match → (None, None) → E3 marca
    `requiere_lectura`. Si hay varios, se toma el MÁXIMO plausible (favorable al paper: si
    ni su mejor cifra supera el listón, el rechazo es seguro). La cita es "abstract" (ubicación
    real, texto no figura) + la frase exacta que hizo match, para auditar.
    """
    abstract = candidate.get("abstract") or ""
    best, best_span = None, None
    for m in _SHARPE_RE.finditer(abstract):
        val = float(m.group(1))
        if _SHARPE_MIN <= val <= _SHARPE_MAX and (best is None or val > best):
            best, best_span = val, m.group(0)
    if best is None:
        return None, None
    return best, f'abstract ("{best_span.strip()}")'


def estimate_fields(candidate: dict) -> dict:
    """Todos los campos deterministas que E3 necesita, desde título + abstract.

    No decide keep/reject (eso es E3); sólo POBLA los campos para que E3 pueda correr.
    """
    text = _text(candidate)
    frec = estimate_frecuencia(text)
    bruto, cita = extract_bruto_reportado(candidate)
    out = {
        "frecuencia": frec,
        "clase_de_dato": estimate_clase(text),
        "duty_cycle_estimado": estimate_duty(text) if frec == "EOD" else None,
        "turnover_estimado": estimate_turnover(text, frec),
        "bruto_reportado": bruto,
        "cita_bruto": cita,
    }
    if frec != "EOD":
        out["trades_por_dia_estimado"] = estimate_trades_por_dia(text, frec)
        out["contrato_ref"] = estimate_contrato(text)
    return out


# ---- fuente: peso para la prioridad (papers arbitrados por delante de blogs) ----
_FUENTE_PESO = {"paper_arbitrado": 0.5, "preprint": 0.3, "blog": 0.1,
                "reddit": 0.05, "twitter": 0.05, "discord": 0.05, "youtube": 0.05}


def priority_score(candidate: dict) -> float:
    """Score determinista para ORDENAR el procesamiento en sesión (mayor = antes).

    Prioriza (en orden de peso): (1) un bruto reportado que YA supera el listón (margen
    de edge sobre el requerido), (2) fuente arbitrada > preprint > blog, (3) frecuencia EOD
    (vehículo conocido/barato) sobre intradía. Los `requiere_lectura` (sin bruto) puntúan por
    fuente/frecuencia y quedan por debajo de los que traen una cifra que despeja — así, si hay
    que cortar por tiempo, se cortan los peores, no los últimos de la lista.
    """
    score = 1.0
    bruto = candidate.get("bruto_reportado")
    req = candidate.get("bruto_requerido_cfd")
    if isinstance(bruto, (int, float)) and isinstance(req, (int, float)):
        score += max(0.0, bruto - req)            # margen de edge (0 si no despeja)
    score += _FUENTE_PESO.get(candidate.get("tipo_de_fuente", ""), 0.0)
    if (candidate.get("frecuencia") or "EOD") == "EOD":
        score += 0.2
    return round(score, 4)
