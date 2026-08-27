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
# número ANTES de "Sharpe": "a 0.55 Sharpe ratio", "0.9 Sharpe" (frase muy común; la run 002 la
# halló en el paper de momentum sectorial). Se excluye si el número lleva '%' (es un retorno).
_SHARPE_RE_PRE = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:annualized\s+|annual\s+|net\s+|gross\s+)?sharpe",
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
    for rx in (_SHARPE_RE, _SHARPE_RE_PRE):
        for m in rx.finditer(abstract):
            # excluir números que en realidad son porcentajes (retornos): "5.99% ... Sharpe"
            if m.group(0).lstrip().startswith(m.group(1)) and _pct_after(abstract, m):
                continue
            val = float(m.group(1))
            if _SHARPE_MIN <= val <= _SHARPE_MAX and (best is None or val > best):
                best, best_span = val, m.group(0)
    if best is None:
        return None, None
    return best, f'abstract ("{best_span.strip()}")'


def _pct_after(text: str, m) -> bool:
    """True si el número casado va inmediatamente seguido de '%' (es un retorno, no un Sharpe)."""
    end = m.start(1) + len(m.group(1))
    return end < len(text) and text[end:end + 1] == "%"


# --- familia_de_riesgo: para no acabar con cuatro versiones de trend (change e3-recalibration) ---
_FAMILIA_RULES = (
    ("trend",          ("momentum", "trend following", "trend-following", "time-series momentum",
                        "time series momentum", "moving average", "breakout")),
    # OJO: "carry" a secas es un VERBO común («pairs carry reversal») → falso positivo. Se exige
    # la familia carry por frases específicas (hallado en el retro-test, change e3-recalibration).
    ("carry",          ("carry trade", "carry strategy", "currency carry", "carry factor",
                        "carry return", "roll yield", "roll-yield", "term premium",
                        "interest rate differential")),
    ("reversion",      ("mean reversion", "mean-reversion", "reversal", "contrarian", "overreaction")),
    ("estacionalidad", ("seasonal", "turn-of-the-month", "turn of the month", "day-of-the-week",
                        "calendar", "holiday", "january effect", "intramonth")),
    ("volatilidad",    ("volatility risk premium", "variance risk premium", "implied volatility",
                        "vix", "straddle", "vol premium", "short vol")),
    ("flujo",          ("order flow", "order-flow", "order imbalance", "volume profile", "vpin",
                        "positioning", "commitment of traders", "microstructure", "footprint")),
    ("macro",          ("macroeconomic", "intermarket", "lead-lag", "monetary policy", "central bank",
                        "yield curve", "inflation")),
)


def estimate_familia_de_riesgo(candidate: dict) -> str:
    """Familia de RIESGO por palabras clave (para medir la diversificación de los supervivientes)."""
    text = _text(candidate)
    for fam, needles in _FAMILIA_RULES:
        if _hits_word(text, needles):
            return fam
    return "otra"


# regex de métricas ALTERNATIVAS para estimar el bruto cuando no hay "Sharpe" (mitiga el problema
# de que arXiv no reporta Sharpe → todo cae en requiere_lectura). Todas anualizadas.
_RET_RE = re.compile(r"(\d+(?:\.\d+)?)\s*%\s*(?:annual(?:ized|ised)?|per\s+year|/\s*year|p\.?a\.?)\s*"
                     r"(?:average\s+)?returns?", re.IGNORECASE)
_VOL_RE = re.compile(r"(?:volatility|standard deviation|annualized vol(?:atility)?)\s*(?:of\s*)?"
                     r"(\d+(?:\.\d+)?)\s*%", re.IGNORECASE)
_IR_RE = re.compile(r"information ratio\s*(?:of|=|:)?\s*(\d+(?:\.\d+)?)", re.IGNORECASE)
_TSTAT_RE = re.compile(r"t-?stat(?:istic)?\s*(?:of|=|:)?\s*(\d+(?:\.\d+)?)", re.IGNORECASE)
_YEARS_RE = re.compile(r"(\d{2,3})\s*years", re.IGNORECASE)


def extract_bruto_estimado(candidate: dict) -> tuple[float | None, str | None]:
    """Estima el bruto anualizado del abstract. Prueba, en orden de fiabilidad:
      (1) "Sharpe ... X"  (directo);           (2) information ratio ≈ Sharpe;
      (3) retorno anual % / vol anual % ;        (4) t-stat / √años.
    Devuelve (bruto, cita con el MÉTODO). Ausente → (None, None). Conservador y auditable."""
    b, c = extract_bruto_reportado(candidate)
    if b is not None:
        return b, c
    abstract = candidate.get("abstract") or ""
    # (2) information ratio ≈ Sharpe
    m = _IR_RE.search(abstract)
    if m and _SHARPE_MIN <= float(m.group(1)) <= _SHARPE_MAX:
        return float(m.group(1)), f'abstract: information ratio ≈ Sharpe ("{m.group(0).strip()}")'
    # (3) retorno anual / vol anual
    mr, mv = _RET_RE.search(abstract), _VOL_RE.search(abstract)
    if mr and mv:
        ret, vol = float(mr.group(1)), float(mv.group(1))
        if vol > 0:
            sr = ret / vol
            if _SHARPE_MIN <= sr <= _SHARPE_MAX:
                return round(sr, 2), f'abstract: ret {ret}% / vol {vol}% → Sharpe {sr:.2f}'
    # (4) t-stat / √años
    mt, my = _TSTAT_RE.search(abstract), _YEARS_RE.search(abstract)
    if mt and my:
        t, yrs = float(mt.group(1)), float(my.group(1))
        if yrs > 0:
            sr = t / (yrs ** 0.5)
            if _SHARPE_MIN <= sr <= _SHARPE_MAX:
                return round(sr, 2), f'abstract: t-stat {t} / √{yrs:.0f}años → Sharpe {sr:.2f}'
    return None, None


def estimate_fields(candidate: dict) -> dict:
    """Todos los campos deterministas que E3 necesita, desde título + abstract.

    No decide keep/reject (eso es E3); sólo POBLA los campos para que E3 pueda correr.
    """
    text = _text(candidate)
    frec = estimate_frecuencia(text)
    # bruto: primero "Sharpe" directo, luego métricas alternativas (IR, ret/vol, t-stat/√años)
    # para que E3 decida más veces en vez de caer siempre en requiere_lectura.
    bruto, cita = extract_bruto_estimado(candidate)
    out = {
        "frecuencia": frec,
        "clase_de_dato": estimate_clase(text),
        "familia_de_riesgo": estimate_familia_de_riesgo(candidate),
        "duty_cycle_estimado": estimate_duty(text) if frec == "EOD" else None,
        "turnover_estimado": estimate_turnover(text, frec),
        "bruto_reportado": bruto,
        "cita_bruto": cita,
    }
    if frec != "EOD":
        out["trades_por_dia_estimado"] = estimate_trades_por_dia(text, frec)
        out["contrato_ref"] = estimate_contrato(text)
    return out


# =====================================================================================
# DÉCIMO EJE — es_estrategia_operable (E2.5, determinista, sobre el abstract)
# =====================================================================================
# La corrida 001 mostró que el modo de muerte DOMINANTE (10 de 11 supervivientes de E2) es
# «esto no es una estrategia operable, es un método / teoría / modelo / monitor». Los 9 ejes
# del adversario (E5) PRESUPONEN que hay estrategia, así que no lo detectan. Este eje va ANTES
# (en E2.5, determinista) para matar ese caso barato y ahorrar ~90% del trabajo de sesión.
#
# Regla: se RECHAZA salvo que el abstract muestre una REGLA DE ENTRADA/SALIDA direccional
# identificable. Dos pasos: (1) descalificadores de ALTA PRECISIÓN (método/teoría/modelo/
# monitor/herramienta) → rechazo; (2) si no, exige al menos una señal de REGLA operable → si
# no hay, rechazo. Calibrado contra las 11 fichas de la run 001 (10 mueren, mean-reversion
# sobrevive) y contra controles positivos (TSMOM/carry/TOM sobreviven). Ver test de regresión.

# (1) descalificadores: el abstract es sobre un MÉTODO/TEORÍA/MODELO/MONITOR/HERRAMIENTA.
# +meta/tooling tras la run 002 (el post de la API de Quantpedia «validaba estrategias», no era una).
_NOT_STRATEGY = (
    "reinforcement learning", "generative model", "flow matching", "generator of", "generation with",
    "simulator", "we simulate", "conditional mean independence", "independence test",
    "we propose a test", "robustness grade", "robustness score", "post-selection robustness",
    "portfolio optimization", "optimal control", "dynamic portfolio", "stochastic control",
    "impulse control", "canonical form", "axiomatic", "latent regularity",
    "spectral radius", "loop gain", "loop-gain", "monitoring",
    "likely outcomes for", "examine the costs", "compare performance", "meld stocks",
    "a python library", "api for", "software",
    "benchmark dataset", "nearest neighbour", "nearest neighbor", "validating new",
)
# (1b) HORIZONTE INOPERABLE (< 1 min): el suelo de costes intradía (docs/cost_floor.md) hace que
# rotar a horizonte de segundos sea inviable a nuestras fees (lección OFI: predictivo a 1s pero
# sub-coste). Un paper cuyo horizonte de posición es sub-minuto se RECHAZA por operabilidad, aunque
# tenga señal (run 002: «Public Trader Identity», R² a 1 s). NO afecta a horizontes ≥ 1 min (la
# mean reversion a 15 min sobrevive).
_INOPERABLE_HORIZON = (
    "millisecond", "microsecond", "nanosecond", "sub-second", "one-second", "1-second",
    "per second", "per-second", "second returns", "second-ahead", "high-frequency", "high frequency",
)
# (2) señales POSITIVAS de una POSICIÓN DIRECCIONAL (verbo de ejecución o familia nombrada).
# Se casan con LÍMITE DE PALABRA (\b): sin él, «carry» casaba dentro de «carrying» y «long the»
# dentro de «along the» (falsos positivos hallados en la run 002 — mismo bug que «ict»⊂«predict»).
# NO basta «predict»/«signal» a secas (lección H003/OFI: PREDECIR ≠ NEGOCIAR).
_STRATEGY_RULE = (
    "go long", "go short", "long-short", "long/short", "buy when", "sell when",
    "betting against", "bet against", "fade", "we trade", "trading rule", "trading strategy",
    "trading signal", "mean reversion", "mean-reversion", "reversal", "momentum",
    "trend following", "trend-following", "carry", "overweight", "underweight", "market timing",
    "rebalance", "rebalancing", "rebalanced", "we buy", "we sell", "long the", "short the",
    "anomaly", "risk premium", "seasonal", "per trade",
)


def _hits_word(text: str, needles) -> str | None:
    """Coincidencia con LÍMITE DE PALABRA: evita que un término corto case dentro de otra palabra
    ('carry' en 'carrying', 'long the' en 'along the'). Multi-palabra también casa con \\b."""
    for n in needles:
        if re.search(r"\b" + re.escape(n) + r"\b", text):
            return n
    return None


def is_operable_strategy(candidate: dict) -> tuple[bool, str]:
    """¿El abstract describe una POSICIÓN DIRECCIONAL a un horizonte operable, o es método/teoría/
    modelo/monitor/herramienta, o una señal a horizonte inoperable?

    Determinista, sobre título+abstract. Refinado tras la run 002 (los 4 falsos positivos
    describían algo MEDIBLE pero no una POSICIÓN, o una posición a horizonte inoperable): (1)
    descalificadores método/teoría/modelo/monitor/tooling; (1b) rechazo por horizonte < 1 min
    (suelo de costes intradía); (2) exige una señal de posición direccional (verbo o familia), con
    límite de palabra. Devuelve (es_estrategia, razón)."""
    text = _text(candidate)
    # REGLA (change pipeline-run-003-and-breadth): TODOS los gates de decisión por palabra clave
    # usan LÍMITE DE PALABRA (\b), sin excepción — tres bugs del mismo tipo (ict⊂predict,
    # carry⊂carrying, long-the⊂along-the) bastan. Ver tests/test_pipeline_word_boundary.py.
    nn = _hits_word(text, _NOT_STRATEGY)
    if nn:
        return False, f"no es estrategia operable: '{nn}' (método/teoría/modelo/monitor/tooling)"
    h = _hits_word(text, _INOPERABLE_HORIZON)
    if h:
        return False, f"horizonte de posición inoperable: '{h}' (< 1 min, sub-coste intradía)"
    p = _hits_word(text, _STRATEGY_RULE)
    if p:
        return True, f"posición direccional identificable ('{p}')"
    return False, "sin posición direccional (dirección + horizonte) identificable en el abstract"


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
