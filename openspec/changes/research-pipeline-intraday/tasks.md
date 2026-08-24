# Tareas

## 1. Esquema — frecuencia y datos
- [x] 1.1 `frecuencia` (EOD|intraday_bar|tick|orderbook) + flags de datos.
- [x] 1.2 `costo_datos_usd_mes`, `trades_por_dia_estimado`, `contrato_ref`,
  `requiere_test_incremental`; estados `rechazada_por_datos`/`rechazada_por_falsabilidad`.

## 2. Estación 3 — suelo de costes intradía
- [x] 2.1 `costs_model.sharpe_bruto_requerido_intraday(trades/día, contrato)` +
  `costo_anual_intraday` + `trades_por_dia_break_1p96`, con specs CME (ES/NQ/CL/GC).
- [x] 2.2 Tabla de referencia y advertencia (crossover vs 1.96%) en `docs/cost_floor.md`.
- [x] 2.3 `triage_costs` enruta por frecuencia (swing por duty vs intradía por rotación).

## 3. Costo de datos como campo de primera clase
- [x] 3.1 Estación 2 rechaza si `costo_datos_usd_mes` > presupuesto ($60 configurable).
- [x] 3.2 Niveles y precios VERIFICADOS documentados (Norgate/IQFeed/Databento, 2026-08-24).

## 4. Falsabilidad + test incremental
- [x] 4.1 Estación 2 rechaza ICT/SMC por no-falsabilidad (filtro #1); admite order flow /
  volume profile / VPIN / microestructura clásica; intradía ya NO se rechaza por omisión.
- [x] 4.2 Flag `requiere_test_incremental` para volume profile + regla documentada.

## 5. Descubrimiento
- [x] 5.1 Barrido de términos de microestructura en arXiv q-fin.TR.

## 6. Backfill + reporte
- [x] 6.1 7 EOD (costo_datos 0) + AMT/volume-profile (rechazada_por_datos) + ICT/SMC
  (rechazada_por_falsabilidad).
- [x] 6.2 Reporte de aprendizaje: distribución por frecuencia y por clase_de_dato.

## 7. Corrección futures_case + tests
- [x] 7.1 `docs/futures_case.md`: Norgate es EOD, no habilita microestructura; precio
  verificado ~$22.50/mes; order flow requiere otro proveedor/presupuesto.
- [x] 7.2 Tests (intradía, falsabilidad, presupuesto, microestructura compite, backfill 9).
  Suite completa verde (137).
