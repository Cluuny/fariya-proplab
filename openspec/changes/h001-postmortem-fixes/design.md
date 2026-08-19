## Context

Ver `proposal.md`. Correcciones al registro de H001 antes de archivar. Números ya verificados contra los datos reales.

## Decisions

### D1 — La degradación se mide intra-muestra en A, no A vs B
A vs B confunde universo (6 vs 9) y período (2004- vs 2015-). El único corte que aísla el tiempo es dentro de A (universo constante). Split en 2016-08 (el pico de la equity): early 2004-2016 Sharpe +0.287 (+30%), late 2016-2026 −0.178 (−17.8%). Eso es la degradación de CXO; el agregado 0.078 promedia los dos regímenes. El reporte reemplaza la línea confundida y añade la tabla del split.

### D2 — Diagnóstico de motor: zero-cost y turnover (calibración reutilizable)
`sharpe_zero_cost = engine.sharpe(backtest(..., apply_costs=False))` y `turnover_anual = sum|Δw|/años`. Resultado: turnover ~9×/año (≈mensual; el ffill sostiene los pesos, el recálculo diario de vol NO infla la rotación) y zero-cost ≈ swap-0.0 → el costo por rotación es pequeño; el efecto en sí es débil (~0.25). Se reporta por muestra. Es calibración que arrastramos a toda hipótesis futura.

### D3 — Nota de max DD/vol como diagnóstico de primera línea
−30.8% de DD con 8.8% de vol (ratio ~3.5×) revienta una barrera del 10% repetidamente aunque el Sharpe fuera 0.5. El falsador de Sharpe es necesario pero no suficiente; para futuras hipótesis, max DD relativo a vol es diagnóstico de primera línea. Se anota en el reporte.

### D4 — Cola y archivo
`hypotheses/QUEUE.md` registra la cola: H001 muerta (archivada), H005 = duplicada de H001 (trend con vol targeting ya implementado) → cerrada. La ficha se mueve a `hypotheses/archive/H001_tsmom.yaml` (estado ya `muerta`, congelado). El archivo de fichas es paralelo al de changes de OpenSpec: la fuente de verdad del veredicto sigue versionada, sólo cambia de carpeta a "cerradas".

## Risks / Trade-offs
- **Split en 2016 es una fecha elegida a posteriori** (el pico) → se reporta como diagnóstico descriptivo, NO como un nuevo test con umbral (no se re-juzga el falsador con él). El veredicto ya está dictado por el agregado.

## Open Questions
- Ninguna.
