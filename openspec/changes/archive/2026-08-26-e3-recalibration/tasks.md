# Tasks

## 1. Factor de degradación
- [x] 1.1 costs_model.FACTOR_DEGRADACION=0.35 (PROVISIONAL) + bruto_efectivo, con derivación
- [x] 1.2 triage_costs aplica bruto_efectivo antes de comparar (EOD + intradía); razones actualizadas

## 2. Listón por estrategia
- [x] 2.1 UMBRAL_NETO=0.40 con la razón nueva (0.4·√4=0.8, cuatro descorrelacionadas)

## 3. familia_de_riesgo
- [x] 3.1 db.py columna + vocab FAMILIAS_DE_RIESGO
- [x] 3.2 estimate.estimate_familia_de_riesgo (fix: 'carry' verbo ≠ familia carry) + wire en estimate_fields
- [x] 3.3 learning_report supervivientes por familia_de_riesgo

## 4. Mitigar (A)
- [x] 4.1 estimate.extract_bruto_estimado (IR / ret-vol / t-stat); reportar fracción rescatada

## 5. Retro-test (sin correr run 003)
- [x] 5.1 scripts/e3_retro.py: re-evaluar los 91 con las reglas nuevas
- [x] 5.2 docs/e3_recalibration.md (derivación, retro-test, reconciliación honesta 1.15↔1.20/1.83)
- [x] 5.3 Actualizar docs/pipeline_walkthrough.md §3 y §6.4

## 6. Verificación
- [x] 6.1 Tests nuevos + fix del test existente; suite verde; holdout intacto; run 003 NO corrida
