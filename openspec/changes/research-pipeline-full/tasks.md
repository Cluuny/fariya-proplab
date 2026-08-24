# Tareas

## Condición de parada y presupuesto
- [x] Escribir `docs/pipeline_stop_condition.md` (textual) ANTES de construir; contador /200.
- [x] Presupuesto $125/mes (estación 2); tabla admite/no-admite con precios verificados 2026-08-24.
- [x] Registrar Databento BANEADO (ToS); no crear cuentas para evadir límites.

## Estación 1 — fuentes no académicas
- [x] `manual_candidate` con `tipo_de_fuente` (reddit/twitter/discord/youtube); MISMOS filtros.
- [x] Tasa de rechazo por tipo de fuente en el learning_report.

## Estación 3 — recalibración
- [x] `LISTONES_REFERENCIA` (CFD 0.64, cripto 0.65, capital propio 0.50 con caveat, duty activo).

## Estaciones 4-7
- [x] 4. `extract.py`: cita por numérico (o null) + sin falsador → rechazo de esquema; seam LLM.
- [x] 5. `adversarial.py`: 8 ejes de ataque; críticos incl. contemporáneo-vs-predictivo y benchmark-cero.
- [x] 6. `stub_gen.py`: stub en signals.py, contrato precios→pesos, NotImplementedError.
- [x] 7. `human_gate.py`: 3-5 candidatos, aprobar UNO → pre_registrado.

## Registro de aprendizaje + backfill
- [x] Campos `tipo_de_fuente`, `causa_de_muerte`, clase `volatilidad_implicita`.
- [x] Consultas SQL: supervivencia por clase y tipo de fuente, calibración, pipeline-vs-reviewer;
  sesgo-a-evitar registrado.
- [x] Backfill 11 (8 con veredicto + H004 + AMT + ICT); reproduce cero supervivientes, 5/8 precio.
- [x] Tests (esquema, estaciones 4-7, backfill/validación). Suite 177 verde.
