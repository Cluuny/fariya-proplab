## 1. Diagnósticos y corrección del reporte

- [x] 1.1 `run_h001.py`: calcular `sharpe_zero_cost` (`apply_costs=False`) y `turnover_anual` (`sum|Δw|/año`) por muestra
- [x] 1.2 `run_h001.py`: split intra-muestra de A (2004-2016 vs 2016-2026, universo constante) con Sharpe por sub-período
- [x] 1.3 `build_report`: reemplazar la línea confundida A-vs-B por la interpretación correcta (confusión universo+período; degradación intra-muestra en A); añadir sección de diagnóstico del motor (zero-cost + turnover) y su lectura (turnover ≈mensual → efecto débil, no rotación); añadir nota de max DD/vol como diagnóstico de primera línea
- [x] 1.4 Correr el runner; verificar el reporte regenerado

## 2. Cola y archivo de H001

- [x] 2.1 `hypotheses/QUEUE.md`: cola con H001 = muerta (archivada) y **H005 = duplicada de H001, cerrada** (misma hipótesis: trend con vol targeting, ya implementada en H001)
- [x] 2.2 Mover `hypotheses/H001_tsmom.yaml` → `hypotheses/archive/H001_tsmom.yaml` (estado ya `muerta`)

## 3. Cierre

- [x] 3.1 Suite verde (`uv run pytest -q`)
- [x] 3.2 Commit
