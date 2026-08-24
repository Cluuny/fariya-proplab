# Tareas

## Bloque A — cerrar la validación (change: ofi-validation-complete)
- [x] A.1 Regresión conjunta ΔP = α + θ_O·OFI + θ_T·TI por media hora, White SE
  (`ols_white_multi`, `joint_regressions`); reportar R²_conj, t de cada coef, %sig.
- [x] A.2 3 días más de regímenes distintos elegidos por vol realizada ANTES del OFI
  (range 02-03, normal 02-12, alta 03-05). Las 4 verificaciones se sostienen en los 4 días.
- [x] A.3 Reportar ĉ y verificar unidades (profundidad implícita vs medida); diagnosticar el
  factor ~5-6× (estable a través de escalas → no es bug de unidades).
- [x] A.4 Deliverable #1 (tabla por día) y #2 (unidades). Hallazgo: TI NO subsumido en cripto.

## Bloque B — curva de decaimiento predictivo (change: ofi-decay-diagnostic)
- [x] B.1 Curva: return futuro ~ OFI a 1s…60min; R², coef, t-White, IC95 block bootstrap,
  n independientes por horizonte.
- [x] B.2 Contemporáneo vs predictivo lado a lado (evitar el error de H003).
- [x] B.3 Cruce con el suelo de costes: Sharpe implícito, rt/día, listón (maker/taker), BRECHA.
- [x] B.4 Criterio de decisión comprometido antes de correr → aplicado.
- [x] B.5 Expectativa comprometida antes de correr → CONFIRMADA.

## Entregables + verificación
- [x] E1 Tests (`test_crypto_decay.py`, +calibrate joint); suite completa 164 verde.
- [x] E2 Deliverables #3 (decaimiento), #4 (gráfico HTML/artifact), #5 (veredicto), #6 (GB/tiempo)
  en `docs/ofi_validation_complete.md`.
- [x] E3 VEREDICTO: ORDER_FLOW_CERRADO. NO modelo de fills, NO pre-registro, NO holdout, NO contratar.
