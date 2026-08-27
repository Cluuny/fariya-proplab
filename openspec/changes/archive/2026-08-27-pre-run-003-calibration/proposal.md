# Dos calibraciones antes de la run 003

## Why

Antes de gastar 4-5 sesiones en las corridas 003-006, dos números baratos cambian el sentido de
hacerlo: (1) el factor de degradación 0.35 gobierna E3 con sólo 3 puntos de calibración; (2) todo
el plan se apoya en 0.4·√4=0.8, y ese √4 exige cuatro estrategias DESCORRELACIONADAS, lo que nunca
se había medido.

## What Changes

Sólo medición + documentación (`docs/pre_run_003_calibration.md`), sin correr la run 003.

1. **Factor de degradación — base ampliada.** Quantpedia NO da pares reportado-vs-realizado en su
   tier gratuito (sólo el paperSharpe agregado como filtro; el realizado es premium; + sesgo de
   selección al alza) → no obtenible. Se ancla en literatura arbitrada (McLean & Pontiff 2016:
   0.74 in-sample-bias / 0.42 post-pub; Chen & Zimmermann ~0.5) + los 3 puntos propios (media 0.35).
   Distribución con mediana de equity ~0.42-0.5; **0.35 es conservador-pero-plausible.** Se
   MANTIENE 0.35 y NO se re-corre el retro-test: es INSENSIBLE al factor en todo el rango (el
   Sectoral muere en E3 para cualquier factor ≤ 0.76; los otros 90 no reportan número). Comentario
   de `costs_model.FACTOR_DEGRADACION` actualizado con la base ampliada.
2. **Diversificación por familia — MEDIDA** (`scripts/family_breadth.py`): series de retorno neto
   de trend (`tsmom`), carry (proxy de tasas × inverse-vol) y estacionalidad (`tom_seasonal`) con
   el motor real; correlación par a par **0.05-0.13 (media 0.09)**, **N_eff de estrategias = 2.95**
   (≈3 ideal), extrapolado a 4 familias **3.91**. **La diversificación existe (ρ~0.09, no 0.6):**
   el multiplicador real es √N_eff ≈ √4, así que 0.40 por estrategia ≈ es correcto (0.47 con 3).
3. **Decisión sobre la run 003: NO correrla.** Umbral final ~1.20 (fut)/~1.83 (CFD); Sharpe
   individual necesario 0.40-0.47 neto; de los 91, **0 supervivientes viables**. A la tasa observada
   (0/91), 200 no alcanza para esperar 4 supervivientes en familias distintas — pero es MOOT: el
   programa ya cerró por amplitud INTRA-familia. Combinar familias funciona; producir UNA que
   despeje el suelo, no.

## Impact

- NUEVO: `scripts/family_breadth.py`, `docs/pre_run_003_calibration.md`,
  `tests/test_family_breadth.py`.
- MOD: `src/costs_model.py` (comentario del factor; valor sin cambio).
- Sin correr la run 003. Holdout intacto. Sin pre-registro. Factor 0.35 sin cambio (justificado).
