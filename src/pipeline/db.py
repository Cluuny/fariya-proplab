"""db.py — el esquema estructurado de la cola de hipótesis (SQLite).

Base de datos ESTRUCTURADA, NO un RAG. La búsqueda vectorial produce un chatbot; lo
que hace falta es una COLA ORDENABLE:

    SELECT * FROM hipotesis WHERE estado='en_cola' ORDER BY score_prioridad DESC LIMIT 1

El esquema reutiliza los campos de la ficha probada en H001/H003/H007 (identidad,
fuente, clasificación, operabilidad, hipótesis testeable, veredicto, cola) y AÑADE el
registro de aprendizaje: clase_de_dato, fuente_de_la_idea, bruto_esperado (committeado
antes de correr), bruto_medido y duty_cycle_real (post-ejecución). Esos campos existen
para preguntar con SQL, no con opiniones: ¿qué clase de dato sobrevive más?, ¿están las
expectativas calibradas o infladas?, ¿las ideas del pipeline sobreviven más que las
humanas? El sistema MIDE la tasa de supervivencia por clase; NO la asume.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

# Ubicación por defecto de la base (regenerable: backfill es determinista).
DEFAULT_DB_PATH = Path("data/pipeline/research.db")

# Vocabularios controlados (documentan los valores válidos; SQLite no los fuerza).
CLASES_DE_DATO = (
    "precio", "macro", "flujo", "fundamental", "estructura_temporal", "calendario",
    "volatilidad_implicita",   # opciones cripto (Deribit/DVOL) — la clase que faltaba desde H004
)
FRECUENCIAS = ("EOD", "intraday_bar", "tick", "orderbook")
FUENTES_DE_LA_IDEA = ("pipeline", "humano", "reviewer")
TIPOS_DE_FUENTE = (
    "paper_arbitrado", "preprint", "blog", "reddit", "twitter", "discord", "youtube",
)
CAUSAS_DE_MUERTE = (
    "coste", "amplitud", "efecto_inexistente", "datos", "falsabilidad", "concentracion",
)
ESTADOS = (
    "candidato",          # recién descubierto, sin triar
    "rechazada_operabilidad",
    "rechazada_por_datos",       # coste de datos > presupuesto, o dato no disponible
    "rechazada_por_falsabilidad",  # no mide un dato externo (ICT/SMC)
    "rechazada_costo",
    "requiere_lectura",   # el abstract no reporta bruto → baja prioridad, no se descarta
    "en_cola",            # pasó los triajes, esperando test
    "pre_registrado",
    "muerta",
    "rechazada",
    "rechazada_coste",
    "cribada_fuera",
    "viable",             # sobrevivió (ninguna hasta hoy)
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS hipotesis (
    id                       TEXT PRIMARY KEY,
    -- identidad / descubrimiento (estación 1)
    titulo                   TEXT NOT NULL,
    abstract                 TEXT,
    url                      TEXT,
    fecha                    TEXT,
    fuente                   TEXT,          -- arxiv | alpha_architect | cxo | ssrn | manual
    fuente_de_la_idea        TEXT,          -- pipeline | humano | reviewer   (registro de aprendizaje)
    tipo_de_fuente           TEXT,          -- paper_arbitrado|preprint|blog|reddit|twitter|discord|youtube
    -- clasificación
    familia                  TEXT,
    mecanismo                TEXT,
    estructura               TEXT,
    direccionalidad          TEXT,
    clase_de_dato            TEXT,          -- precio|macro|flujo|fundamental|estructura_temporal|calendario
    -- frecuencia / requisitos de datos (intradía y microestructura)
    frecuencia               TEXT,          -- EOD | intraday_bar | tick | orderbook
    requiere_volumen_consolidado INTEGER,   -- 0/1 (FX spot NO lo tiene; futuros SÍ)
    requiere_cinta_tick      INTEGER,       -- 0/1
    requiere_order_book_l2   INTEGER,       -- 0/1
    costo_datos_usd_mes      REAL,          -- coste de datos de PRIMERA CLASE
    -- operabilidad (estación 2)
    n_instrumentos           INTEGER,
    frecuencia_datos         TEXT,          -- (legado; descripción libre)
    datos_requeridos         TEXT,          -- JSON list
    operable_en_prop         INTEGER,       -- 0/1
    requiere_test_incremental INTEGER,      -- 0/1 (volume profile: vs niveles simples)
    triage_operabilidad      TEXT,          -- keep | reject
    triage_operabilidad_razon TEXT,
    -- triaje de costos (estación 3)
    duty_cycle_estimado      REAL,
    turnover_estimado        REAL,
    trades_por_dia_estimado  REAL,          -- para el suelo INTRADÍA (round-trips/día)
    contrato_ref             TEXT,          -- ES|NQ|CL|GC para el suelo intradía
    bruto_reportado          REAL,          -- NULL si el abstract no lo dice
    bruto_requerido_cfd      REAL,
    bruto_requerido_futuros  REAL,
    bruto_requerido_intraday REAL,
    triage_costo             TEXT,          -- keep | reject | requiere_lectura
    triage_costo_razon       TEXT,
    -- hipótesis testeable / veredicto (backfill de las ya testeadas)
    hipotesis                TEXT,
    falsador                 TEXT,
    metrica_exito            TEXT,
    holdout                  TEXT,
    -- registro de aprendizaje (los tres números que calibran el programa)
    bruto_esperado           REAL,          -- committeado ANTES de correr
    bruto_medido             REAL,          -- post-ejecución
    duty_cycle_real          REAL,          -- post-ejecución
    causa_de_muerte          TEXT,          -- coste|amplitud|efecto_inexistente|datos|falsabilidad|concentracion
    veredicto                TEXT,
    -- estaciones 4-5 (extracción / revisión adversaria)
    cita_bruto               TEXT,          -- ubicación (sección/tabla) del bruto extraído; sin cita → null
    adversarial_veredicto    TEXT,          -- keep | reject (estación 5)
    adversarial_razon        TEXT,
    -- cola
    score_prioridad          REAL,
    estado                   TEXT NOT NULL DEFAULT 'candidato',
    fecha_test               TEXT,
    created_at               TEXT DEFAULT (datetime('now')),
    updated_at               TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_estado   ON hipotesis(estado);
CREATE INDEX IF NOT EXISTS idx_clase    ON hipotesis(clase_de_dato);
CREATE INDEX IF NOT EXISTS idx_fuente   ON hipotesis(tipo_de_fuente);
CREATE INDEX IF NOT EXISTS idx_prioridad ON hipotesis(estado, score_prioridad);
"""

# Condición de parada del pipeline (docs/pipeline_stop_condition.md).
N_CONDICION_PARADA = 200

# Columnas que aceptan una lista y se guardan como JSON.
_JSON_COLS = {"datos_requeridos"}


def connect(path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Open (creating parent dirs) a SQLite connection with row access by name."""
    p = Path(path)
    if p != Path(":memory:") and str(p) != ":memory:":
        p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(p))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """Create the schema if absent (idempotent)."""
    conn.executescript(SCHEMA)
    conn.commit()


def _valid_columns(conn: sqlite3.Connection) -> set[str]:
    cur = conn.execute("PRAGMA table_info(hipotesis)")
    return {row[1] for row in cur.fetchall()}


def upsert(conn: sqlite3.Connection, record: dict) -> None:
    """Insert or update one hypothesis row by `id`.

    Unknown keys are ignored (so callers can pass a superset). List values on JSON
    columns are serialized. `updated_at` is refreshed on every write.
    """
    if "id" not in record or not record["id"]:
        raise ValueError("upsert requires a non-empty 'id'")
    cols = _valid_columns(conn)
    data = {}
    for k, v in record.items():
        if k not in cols:
            continue
        if k in _JSON_COLS and isinstance(v, (list, tuple)):
            v = json.dumps(list(v))
        if isinstance(v, bool):
            v = int(v)
        data[k] = v
    exists = conn.execute("SELECT 1 FROM hipotesis WHERE id=?", (data["id"],)).fetchone()
    if exists:
        # UPDATE only the provided columns — a partial update (e.g. a triage step) must
        # NOT re-assert NOT NULL columns like `titulo` that it doesn't carry.
        cols = [k for k in data if k != "id"]
        if not cols:
            return
        set_clause = ", ".join(f"{k}=?" for k in cols) + ", updated_at=datetime('now')"
        conn.execute(f"UPDATE hipotesis SET {set_clause} WHERE id=?",
                     [data[k] for k in cols] + [data["id"]])
    else:
        keys = list(data)
        placeholders = ", ".join("?" for _ in keys)
        conn.execute(
            f"INSERT INTO hipotesis ({', '.join(keys)}, updated_at) "
            f"VALUES ({placeholders}, datetime('now'))",
            [data[k] for k in keys])
    conn.commit()


def get(conn: sqlite3.Connection, hyp_id: str) -> dict | None:
    row = conn.execute("SELECT * FROM hipotesis WHERE id=?", (hyp_id,)).fetchone()
    return dict(row) if row else None


def next_in_queue(conn: sqlite3.Connection) -> dict | None:
    """The highest-priority hypothesis waiting to be tested (the ordered queue)."""
    row = conn.execute(
        "SELECT * FROM hipotesis WHERE estado='en_cola' "
        "ORDER BY score_prioridad DESC NULLS LAST, id ASC LIMIT 1"
    ).fetchone()
    return dict(row) if row else None


def all_rows(conn: sqlite3.Connection) -> list[dict]:
    return [dict(r) for r in conn.execute("SELECT * FROM hipotesis ORDER BY id").fetchall()]


def count_processed(conn: sqlite3.Connection) -> int:
    """Candidatos PROCESADOS (atravesaron al menos el triaje): estado != 'candidato'.
    Es el numerador de la condición de parada (procesados / N_CONDICION_PARADA)."""
    return conn.execute(
        "SELECT COUNT(*) FROM hipotesis WHERE estado != 'candidato'").fetchone()[0]
