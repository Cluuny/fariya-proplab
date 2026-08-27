# Corrida 002 — eje operabilidad + rebalanceo de fuentes

## Why

La corrida 001 mostró dos cosas accionables: (a) el modo de muerte DOMINANTE (10 de 11
supervivientes de E2) fue «esto no es una estrategia operable, es método/teoría/modelo/
monitor» — un hueco fuera de los 9 ejes del adversario; y (b) la corrida fue ~95% arXiv, que
resultó ser mayoritariamente metodología. Esta corrida arregla ambas: un DÉCIMO EJE
determinista que mata el no-estrategia barato (ahorra ~90% del trabajo de sesión) y un
REBALANCEO de fuentes hacia trabajo aplicado (Quantpedia, RSS), midiendo la DENSIDAD de
estrategias operables por fuente — el número que dice dónde buscar.

## What Changes

1. **Décimo eje `es_estrategia_operable` en E2.5** (`src/pipeline/estimate.py`, determinista,
   sobre el abstract, ANTES del adversario que presupone estrategia). Rechaza salvo que el
   abstract muestre una REGLA de entrada/salida direccional. Regla clave: exige un VERBO DE
   EJECUCIÓN o una familia nombrada — «predict»/«signal» a secas NO bastan (lección propia
   H003/OFI: predecir ≠ negociar). Test de regresión: los 10 no-estrategias de la run 001
   mueren en E2.5 y el candidato de mean reversion sobrevive.
2. **Rebalanceo de fuentes en E1** (`discover.py`): +Quantpedia RSS (estrategias ya
   destiladas → mayor densidad esperada); arXiv con cuota reducida; se procesan las fuentes
   NO-arXiv primero (RSS/Quantpedia) y arXiv rellena → arXiv toma la cuota menor. SSRN no tiene
   API pública → ingesta manual (no se puede subir automáticamente; se anota).
3. **Métrica nueva: DENSIDAD de estrategias operables por fuente** = pasan es_estrategia_operable
   / descubiertos (`learning_report._densidad_estrategia_por_fuente`). Se reporta por fuente.
4. **Correr run 002**, 40 candidatos nuevos (contador → 91/200), DB PERSISTENTE sembrada con
   la run 001 para que el contador acumule honestamente. Entregable D1-D7 en
   `docs/pipeline_run_002.md`.
5. **Registrar validación externa en `program_verdict.md`**: arxiv:2608.21888 (mean reversion
   15 min en cripto, de la run 001) mide el mismo muro coste-supera-señal que el programa
   encontró con OFI (ratio 0.009-0.039) y H008 — primera validación externa de una CONCLUSIÓN
   propia, no sólo del motor.

Defectos deterministas hallados por la corrida y corregidos (con test): la extracción del
Sharpe no capturaba el número ANTES de «Sharpe» («0.55 Sharpe ratio») → arreglado, con guardia
anti-porcentaje. **NO se pre-registra ninguna hipótesis — sólo se producen candidatos.**

## Impact

- MOD: `estimate.py` (eje + extracción pre-Sharpe), `discover.py` (Quantpedia), `db.py`
  (estado `rechazada_no_estrategia` + causa `no_estrategia`), `scripts/pipeline.py` (eje en
  cmd_triage), `learning_report.py` (densidad).
- NUEVO: `scripts/pipeline_run_002.py`, `tests/test_pipeline_strategy_axis.py`,
  `docs/pipeline_run_002.md`. MOD `docs/program_verdict.md` (validación externa).
- DB `data/pipeline/research.db` (gitignored, persistente): counter 51 → 91 / 200.
- Sin API cableada, holdout intacto, sin pre-registro.
