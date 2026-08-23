## Why

Dos cosas: (1) corregir un error de framing en `cot_coverage.md`/`queue_triage.md` — "duty bajo baja el listón" es FALSO; y (2) cribar el efecto COT con los datos ya ingeridos ANTES de pre-registrar nada.

## What Changes

- **CORRECCIÓN**: `costs_model.sharpe_activo_requerido(duty) = 0.40/√duty + 0.245` (duty 100%→0.645, 20%→1.14, 10%→1.51). Bajar el duty SUBE el listón en señal activa (el bruto de serie completa se diluye ∝√duty). Se corrigen `data/cot_coverage.md` y `docs/queue_triage.md`. El TRIAJE de H002/H005/H006 se MANTIENE; sólo cambia la justificación: cae "duty bajo baja el listón" (falso), se mantiene "información no-de-precio". **H002: motivo PRINCIPAL de rechazo pasa a CONCENTRACIÓN** (N_eff 3.41, short-JPY, prima de crash), no coste; su neto 0.282 (el mejor del proyecto) muere por umbral, no por falsador.
- **CRIBADO** (`scripts/cot_screen.py` + `docs/cot_diagnostic.md`): para los 8 instrumentos con COT, retorno futuro (1/2/4 sem) condicionado al percentil rodante (3 años), Sharpe activo del fade en extremos (p10/90, p5/95), con: Sharpe por instrumento y agrupado + IC 95%; n EFECTIVO por EPISODIOS (no días); bootstrap POR EPISODIO; y verificación del signo.

## Resultado — COT MUERE sin pre-registro

Expectativa comprometida: Sharpe activo 0.4-0.8. Resultado: **agrupado ≈ 0** (2s −0.02 IC[−0.42,+0.34]; 1s −0.29; 4s −0.04), IC cruza 0, y el **signo del mecanismo falla en 5/8** (specs acertaron = momentum, no reversión). n episodios 43-118/instrumento (>30) → cero real, no falta de poder. Sharpe activo < 0.7 → por el criterio comprometido, **COT no se pre-registra**, como H005/H006. Incluso más débil que lo esperado. El argumento no-de-precio sigue siendo válido, pero el efecto no está a resolución semanal/EOD en estos 8.

## Capabilities

### New/Modified Capabilities
<!-- Ninguna: corrección de doc + cribado. skip_specs=true. -->

## Impact

- `src/costs_model.py` (+sharpe_activo_requerido), `tests/test_costs_model.py` (+1), `scripts/cot_screen.py`, `docs/cot_diagnostic.md`, correcciones a `data/cot_coverage.md`/`docs/queue_triage.md`/`QUEUE.md`. Sin pre-registrar H008.
