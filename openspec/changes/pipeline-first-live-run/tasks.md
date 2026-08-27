# Tasks

## 1. Convertir E2/E3 a heurística determinista (pre-corrida)
- [x] 1.1 `src/pipeline/estimate.py`: `estimate_fields(cand)` → frecuencia, duty_cycle_estimado, turnover_estimado, clase_de_dato, trades_por_dia_estimado, contrato_ref, bruto_reportado + cita_bruto (regex sobre abstract; ausente → None)
- [x] 1.2 `estimate.priority_score(cand)` determinista (para ordenar el procesamiento en sesión)
- [x] 1.3 Fix `discover.py`: `ARXIV_API` http → https
- [x] 1.4 Wire en `scripts/pipeline.py cmd_triage`: E2 keep → estimar+persistir → E3 → score
- [x] 1.5 Tests de `estimate` (frecuencia, duty, extracción de Sharpe con/sin cita, prioridad)

## 2. Corrida E1-E3 (batch determinista, cap 40)
- [x] 2.1 `scripts/pipeline_run_001.py`: E1 (arXiv 3 cats + microestructura + RSS), cap 40 candidatos procesados
- [x] 2.2 Correr E1-E3 contra la DB real; registrar embudo por estación y por tipo de fuente
- [x] 2.3 Listar supervivientes de E3 (en_cola + requiere_lectura) por prioridad desc

## 3. E4-E5 en sesión (solo supervivientes)
- [x] 3.1 Extracción (E4) en sesión con reglas anti-alucinación (cita-o-null, figura→null, sin-falsador→rechazo)
- [x] 3.2 Adversario (E5) con los 9 ejes incl. `nulo_preserva_geometria`; llenar `hallazgo_no_enumerado`
- [x] 3.3 Persistir veredictos en la DB

## 4. Lectura humana (proxy) + métrica de alcance del adversario
- [x] 4.1 Pase de lectura cuidadosa sobre los que llegan a la compuerta; registrar problemas que el adversario NO reportó

## 5. Entregable + docs
- [x] 5.1 `docs/pipeline_run_001.md` D1-D7 autosuficiente
- [x] 5.2 Nota en `docs/research_pipeline.md` (no automatizable en modo sesión) + `docs/extraction_defects.md` (métrica adversario-vs-operador)
- [x] 5.3 Suite verde

## 6. Verificación
- [x] 6.1 Contador de parada correcto (11 → ≤51 / 200), holdout intacto, sin pre-registro, sin API cableada
