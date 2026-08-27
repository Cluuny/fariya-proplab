# Tasks

## 1. Décimo eje es_estrategia_operable (E2.5, determinista)
- [x] 1.1 `estimate.is_operable_strategy` (descalificadores método/teoría/modelo/monitor + gate de regla operable; predecir≠negociar)
- [x] 1.2 Wire en `scripts/pipeline.py cmd_triage` (E2 keep → eje → estimate → E3); estado `rechazada_no_estrategia` + causa `no_estrategia`
- [x] 1.3 Test de regresión: run 001 → 10 mueren en E2.5, mean reversion sobrevive; controles positivos + predicción-sola muere

## 2. Rebalanceo de fuentes (E1)
- [x] 2.1 +Quantpedia RSS en `discover.RSS_FEEDS`
- [x] 2.2 `scripts/pipeline_run_002.py`: DB persistente sembrada con run 001; arXiv cuota reducida; no-arXiv primero

## 3. Métrica de densidad
- [x] 3.1 `learning_report._densidad_estrategia_por_fuente` + sección en el reporte

## 4. Correr run 002
- [x] 4.1 Correr E1-E3 (cap 40, contador 91/200); embudo + densidad por fuente
- [x] 4.2 E4-E5 en sesión sobre supervivientes (reglas anti-alucinación + 9 ejes)

## 5. Entregable + validación externa
- [x] 5.1 `docs/pipeline_run_002.md` D1-D7 autosuficiente + densidad
- [x] 5.2 `docs/program_verdict.md`: validación externa (arxiv:2608.21888 vs OFI/H008)
- [x] 5.3 Suite verde

## 6. Verificación
- [x] 6.1 Contador 91/200, holdout intacto, sin pre-registro, sin API cableada
