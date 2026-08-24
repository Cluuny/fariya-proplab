# Extender el pipeline a intradía y microestructura

## Por qué

El pipeline asumía frecuencia EOD implícitamente. Las hipótesis de microestructura (order
flow, volume profile, AMT) quedaban fuera **por omisión, no por evaluación**. Deben
**competir en igualdad**, con su listón de costos correcto — o ser rechazadas por una razón
explícita (datos o falsabilidad), no por un hueco del diseño.

## Qué cambia

1. **Esquema**: `frecuencia` (EOD|intraday_bar|tick|orderbook), flags de datos
   (`requiere_volumen_consolidado`/`_cinta_tick`/`_order_book_l2`), `costo_datos_usd_mes`,
   `trades_por_dia_estimado`, `contrato_ref`, `requiere_test_incremental`.
2. **Estación 3 → intradía**: `costs_model.sharpe_bruto_requerido_intraday(trades/día,
   contrato)` — en intradía el coste lo domina ROTAR. Calibrado con specs CME reales
   (ES/NQ/CL/GC) + comisión IBKR. Tabla de referencia y advertencia en `docs/cost_floor.md`:
   por encima de ~1.4 round-trips/día en ES (0.4 en CL) el coste supera el 1.96%/año del
   margen CFD que mató seis hipótesis. La estación 3 enruta por frecuencia.
3. **Costo de datos de primera clase**: la estación 2 rechaza si excede el presupuesto
   ($60/mes por defecto). Niveles documentados con **precios verificados** (Norgate
   ~$22.50/mes EOD; IQFeed ~$133/mes 1-min+tick; Databento Plus ~$1 750/mes L2/L3).
4. **Falsabilidad (filtro #1)**: la estación 2 rechaza ICT/SMC (order blocks, FVG) por no
   medir un dato externo — distinción de CATEGORÍA. Admite order flow / volume profile /
   VPIN / microestructura clásica. La microestructura intradía ya NO se rechaza por omisión.
5. **Test incremental para volume profile**: requisito de diseño (`requiere_test_incremental`)
   — medir el aporte del VAH/VAL/POC SOBRE niveles simples, no en absoluto.
6. **Descubrimiento**: barrido de términos de microestructura en arXiv q-fin.TR.
7. **Backfill**: las 7 EOD (costo_datos 0) + AMT/volume profile (`rechazada_por_datos`, con
   proveedor y precio) + ICT/SMC (`rechazada_por_falsabilidad`). Reporte de aprendizaje con
   distribución por frecuencia.
8. **Corrección en `docs/futures_case.md`**: Norgate es EOD → el mes planeado NO habilita
   order flow ni volume profile intradía; eso requiere otro proveedor y otro presupuesto.

## Impacto

- `src/costs_model.py` (funciones intradía), `src/pipeline/` (db/triage_costs/
  triage_operability/discover/backfill/learning_report), `scripts/pipeline.py`,
  `tests/test_pipeline.py`, docs (`cost_floor.md`, `futures_case.md`, `research_pipeline.md`).
- Stdlib only, sin nuevas deps. Suite completa verde (137). Sin delta de spec.
- Precios verificados vía web (Norgate/IQFeed/Databento), consulta 2026-08-24.
