# Tasks

## 1. Calibrar el factor de degradación con más puntos
- [x] 1.1 Intentar Quantpedia (tier gratuito) — documentar que NO da pares reportado/realizado (+ sesgo)
- [x] 1.2 Base ampliada: literatura (McLean-Pontiff, Chen-Zimmermann) + 3 puntos propios; distribución
- [x] 1.3 Decidir: 0.35 se mantiene (conservador, plausible); INMATERIAL para los 91 → no re-correr retro
- [x] 1.4 Actualizar comentario de costs_model.FACTOR_DEGRADACION

## 2. Verificar la diversificación por familia
- [x] 2.1 scripts/family_breadth.py: series netas trend/carry/estacionalidad con el motor real
- [x] 2.2 Correlación par a par + N_eff de ESTRATEGIAS (participation ratio) + multiplicador real
- [x] 2.3 Sharpe individual necesario para 0.8 (3 y 4 familias)

## 3. Decisión sobre la run 003
- [x] 3.1 Umbral final, Sharpe individual necesario, cuántos de 91 sobreviven
- [x] 3.2 Estimación: candidatos para 4 supervivientes en familias distintas; ¿200 alcanza?
- [x] 3.3 Veredicto: NO correr la run 003

## 4. Entregable + verificación
- [x] 4.1 docs/pre_run_003_calibration.md
- [x] 4.2 Tests (N_eff, carry proxy); suite verde; holdout intacto; run 003 NO corrida
