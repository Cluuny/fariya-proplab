## Context

Ver `proposal.md`. `src/report.py` ya provee `metrics`, `equity_curve`, `max_drawdown`, `return_distribution` y `render/generate` (markdown determinista → `results/<name>/report.md`). El runner de H001 no los usaba.

## Decisions

### D1 — El runner arma el reporte y reutiliza `report.py`
`run_h001.py` construye un `results/H001/report.md` con: (a) cabecera de veredicto + contrato congelado; (b) la tabla Sharpe neto muestra × swap; (c) interpretación (regla de dos muestras, sensibilidad al swap, costo dominante); (d) por muestra, sobre la especificación primaria (swap 0.3), el bloque de métricas de `report.metrics` + equity muestreada + `max_drawdown` + `return_distribution`. Reusa los helpers de `report.py` en vez de duplicar el cálculo.

### D2 — Determinista, sin timestamps
Igual que `report.render`: sin `datetime.now()`. La `fecha_test` es un dato del contenido (2026-08-18), no el tiempo de generación. Así el reporte es diffable y reproducible: misma data → mismo archivo.

### D3 — Persistencia bajo `results/` (gitignoreado)
`results/` ya está en `.gitignore` (resultados reproducibles no se versionan; el veredicto sí vive versionado en la ficha YAML). El reporte se regenera con un comando. Coherente con `data/quality_report.md` (también gitignoreado, regenerable).

## Risks / Trade-offs
- **El reporte no se versiona** → correcto: es derivado. La fuente de verdad del veredicto es `hypotheses/H001_tsmom.yaml` (versionado). El reporte es la vista legible, regenerable.

## Open Questions
- Ninguna.
