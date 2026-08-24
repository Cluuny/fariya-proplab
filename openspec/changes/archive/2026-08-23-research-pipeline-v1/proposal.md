# Esqueleto del pipeline de investigación (Flujo 2, estaciones 1-3)

## Por qué

Las siete hipótesis del proyecto vinieron de **una sola fuente** (el reviewer); cinco de
siete fueron precio puro; nunca se leyó un paper completo. Esa dependencia de fuente única
es un **fallo estructural** tan importante como el suelo de costes. El pipeline le da al
sistema un flujo propio de candidatos, un filtro barato y un registro de aprendizaje que
**mide** (no asume) qué clase de idea sobrevive.

## Qué cambia

Corrección de arquitectura vs. el diseño de junio: el filtro que más mata es la
**aritmética de costos** (H005/H006 murieron sin correrse), así que va ANTES de leer el
paper. Orden nuevo: 1) Descubrimiento → 2) Operabilidad → **3) Costos** → (4-7 fuera de
alcance).

- **Estación 1 — Descubrimiento** (`src/pipeline/discover.py`): arXiv API (q-fin.*) + RSS
  (Alpha Architect, CXO) + ingesta manual SSRN. Parseo puro y testeable; fetch aislado;
  fuente caída no tumba el resto. Cron **mensual**.
- **Estación 2 — Operabilidad** (`triage_operability.py`): rechaza cross-sectional de
  acciones, opciones/vol implícita, fundamentales, intradía, o sin regla identificable.
  Heurística determinista con seam para un modelo (LLM fuera de alcance).
- **Estación 3 — Costos** (`triage_costs.py`): reutiliza
  `costs_model.sharpe_bruto_requerido_duty`; rechaza si `bruto_reportado` no supera el
  requerido; `requiere_lectura` si el abstract no reporta bruto. **Parametrizado por
  vehículo** (CFD 0.64 / futuros 0.424).
- **Esquema** (`db.py`): SQLite estructurado (cola ordenable, NO un RAG). Reutiliza los
  campos de la ficha H001/H003/H007 y añade el **registro de aprendizaje**:
  `clase_de_dato`, `fuente_de_la_idea`, `bruto_esperado`, `bruto_medido`, `duty_cycle_real`.
- **Backfill** (`backfill.py`): las 7 hipótesis conocidas como conjunto de validación.
  Reproduce cero supervivientes y 5/7 precio.
- **Reporte de aprendizaje** (`learning_report.py`): distribución + supervivencia por clase
  y calibración de expectativas, con SQL. **Sin sesgo pro-macro**: la supervivencia se mide.
- **CLI** (`scripts/pipeline.py`), tests (`tests/test_pipeline.py`), doc
  (`docs/research_pipeline.md`).

## Impacto

- Nuevo paquete `src/pipeline/`, script `scripts/pipeline.py`, doc, tests. Sin nuevas
  dependencias (stdlib: sqlite3, urllib, xml). DB regenerable (gitignored).
- Alcance acotado: estaciones 1-3 + esquema + aprendizaje + backfill. NO LLM, NO revisión
  adversaria, NO stubs — sólo si el mes de futuros da luz verde. Presupuesto ~8-10 h.
- Sin cambio de comportamiento en el motor/estrategias existentes; sin delta de spec.
