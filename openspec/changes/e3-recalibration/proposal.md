# Recalibrar E3 antes de correr hasta los 200

## Why

`docs/pipeline_walkthrough.md` §3/§6.4 documentaron dos problemas de E3: (A) mató 0 en ambas
corridas (los abstracts no reportan Sharpe → todo `requiere_lectura`, no ahorra sesión); (B)
cuando decide, compara el bruto REPORTADO (in-sample, sin deflactar, otro mercado) contra el
listón sin descontar — el Sectoral pasó con 0.55 y murió después en el cribado con IC95 [0.17,0.93].
Hay que recalibrar E3 ANTES de gastar la run 003, y validarlo con un retro-test sobre lo ya
procesado.

## What Changes

1. **Factor de degradación** (`costs_model.FACTOR_DEGRADACION = 0.35`, PROVISIONAL, calibrado con
   evidencia propia: TSMOM 1.2→0.37, TOM ~0, Sectoral 0.55→~0.4). E3 aplica `bruto_efectivo =
   reportado × 0.35` antes de comparar contra el requerido (que ya lleva el suelo de costes). Un
   paper necesita reportar ~1.20 (futuros) / ~1.83 (CFD) para sobrevivir. (El ~1.15 del bloque = el
   umbral de futuros; comparar contra el 0.40 neto directo saltaría el suelo de costes — el factor
   es reportado→bruto, no reportado→neto.)
2. **UMBRAL_NETO = 0.40 con razón nueva:** 0.4 neto POR ESTRATEGIA, porque el objetivo son CUATRO
   estrategias DESCORRELACIONADAS (0.4·√4 = 0.8) — la única amplitud que el terreno no agota.
3. **Campo `familia_de_riesgo`** (`db.py` + `estimate.estimate_familia_de_riesgo` +
   `learning_report._por_familia_riesgo`): para no acabar con cuatro versiones de trend; la
   diversificación se mide. (Corregido un falso positivo: «carry» verbo ≠ familia carry.)
4. **Mitigar (A):** `estimate.extract_bruto_estimado` intenta IR / ret-vol / t-stat cuando no hay
   Sharpe directo. Retro-test: rescató 0/80 (los abstracts no las traen; honesto).
5. **Retro-test** (`scripts/e3_retro.py`) sobre los 91 ya procesados: con la regla nueva **el
   Sectoral muere en E3** (no en el cribado posterior), 1 rechazo determinista (antes 0),
   supervivientes por familia = {reversion: 1}. NO se corre la run 003.

## Impact

- MOD: `src/costs_model.py`, `src/pipeline/triage_costs.py` (degradación + razón UMBRAL_NETO),
  `src/pipeline/estimate.py` (familia + métricas alternativas), `src/pipeline/db.py`
  (familia_de_riesgo), `src/pipeline/learning_report.py` (query), `docs/pipeline_walkthrough.md`
  (§3/§6.4), + fix de un test existente.
- NUEVO: `scripts/e3_retro.py`, `docs/e3_recalibration.md`, `tests/test_e3_recalibration.py`.
- Holdout intacto, sin pre-registro, sin correr la run 003. Factor PROVISIONAL. Suite 251 verde.
