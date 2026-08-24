# Tareas

## 1. Esquema estructurado (SQLite, no RAG)
- [x] 1.1 `src/pipeline/db.py`: tabla `hipotesis` reutilizando los campos de la ficha
  H001/H003/H007 + cola ordenable (`next_in_queue`).
- [x] 1.2 Campos nuevos del registro de aprendizaje: `clase_de_dato`, `fuente_de_la_idea`,
  `bruto_esperado`, `bruto_medido`, `duty_cycle_real`.
- [x] 1.3 `upsert` con update parcial (no re-asserta NOT NULL en updates de triaje), JSON
  para listas, idempotente.

## 2. Estación 1 — Descubrimiento
- [x] 2.1 `discover.py`: arXiv API (q-fin.PM/ST/TR) con parseo Atom puro.
- [x] 2.2 RSS de Alpha Architect y CXO (parseo RSS puro).
- [x] 2.3 SSRN por ingesta manual (`manual_candidate`).
- [x] 2.4 Orquestación robusta (fuente caída no tumba el resto) + nota de cron MENSUAL.

## 3. Estación 2 — Triaje de operabilidad
- [x] 3.1 Reglas de rechazo: cross-sectional acciones (>100), opciones, fundamentales,
  intradía, sin regla identificable.
- [x] 3.2 Heurística determinista con seam para un modelo (LLM fuera de alcance); keep/reject + razón.

## 4. Estación 3 — Triaje de costos (el filtro nuevo)
- [x] 4.1 Reutilizar `costs_model.sharpe_bruto_requerido_duty`; parametrizar por vehículo
  (CFD 0.64 / futuros 0.424).
- [x] 4.2 reject si bruto_reportado no supera; `requiere_lectura` si no hay bruto.

## 5. Backfill + reporte de aprendizaje
- [x] 5.1 `backfill.py`: las 7 hipótesis (H001,H002,H003,H005,H006,H007,COT), fuente=reviewer.
- [x] 5.2 Reproduce los veredictos conocidos: cero supervivientes, 5/7 precio.
- [x] 5.3 `learning_report.py`: distribución + supervivencia por clase + calibración, con SQL;
  SIN sesgo pro-macro (la supervivencia se MIDE).

## 6. CLI, tests, docs
- [x] 6.1 `scripts/pipeline.py` (init/backfill/discover/triage/report/queue).
- [x] 6.2 `tests/test_pipeline.py` (esquema, reglas de ambos triajes, parseo sobre fixtures,
  backfill/validación, reporte). Suite completa verde.
- [x] 6.3 `docs/research_pipeline.md`; gitignore de la DB regenerable.
