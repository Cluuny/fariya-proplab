# Pipeline de investigación COMPLETO (estaciones 1-7)

## Por qué

Siete de las ocho familias con veredicto salieron del reviewer; cinco de ocho fueron precio
puro; nunca se leyó un paper completo. Esa dependencia de una sola fuente de ideas es un fallo
del programa, tan real como el suelo de costes. El pipeline existe para romperla y se juzga
por si produce supervivientes que el reviewer NO habría propuesto.

## Qué cambia

- **Condición de parada** (`docs/pipeline_stop_condition.md`, escrita antes de construir):
  200 candidatos procesados; contador visible en el reporte. Presupuesto $125/mes.
- **Presupuesto de datos $125/mes** (estación 2): admite Norgate (~$50), Binance (gratis),
  **Deribit opciones cripto (gratis) — reabre volatility risk premium**, BIS/FRED/CFTC/LOBSTER
  (gratis). NO admite opciones de acciones, Databento ($199/$1750, **BANEADO por ToS**),
  Polygon ($199), IQFeed (~$133, frontera). Precios verificados 2026-08-24.
- **Estación 1 — fuentes no académicas**: Reddit/Twitter/Discord/YouTube por ingesta manual,
  MISMOS filtros; tasa de rechazo por tipo de fuente como resultado.
- **Estación 3 recalibrada**: listones de ambos ciclos (CFD 0.64, cripto 0.65, capital propio
  0.50 con caveat de leverage, duty activo).
- **Estaciones 4-7**: extracción (`extract.py`, dos reglas anti-alucinación: cita por numérico
  o null; sin falsador → rechazo de esquema), revisión adversaria (`adversarial.py`, 8 ejes,
  lecciones H003/OFI como críticos), generación de stub (`stub_gen.py`, contrato precios→pesos),
  compuerta humana (`human_gate.py`).
- **Registro de aprendizaje**: campos `tipo_de_fuente`, `causa_de_muerte`, clase
  `volatilidad_implicita`; consultas SQL incl. **supervivencia pipeline vs reviewer** (el test
  de si valió la pena) y el sesgo-a-evitar registrado.
- **Backfill (11)**: 8 con veredicto + H004 (datos, reabierta por Deribit) + AMT + ICT.
  Reproduce cero supervivientes, 5/8 precio, 8/8 reviewer.

## Impacto

- `src/pipeline/` (db, discover, triage_*, backfill, learning_report + extract, adversarial,
  stub_gen, human_gate), docs, tests. Sin nuevas deps (LLM de estaciones 4-5 como seam). Suite
  177 verde. Sin delta de spec. Infra/cribado: no consume intentos, no toca holdout.
