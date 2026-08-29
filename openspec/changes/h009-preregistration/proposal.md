# Pre-registro H009 — AMT continuación (aceptación fuera del área de valor)

## Why

H008 probó la cara de FADE de AMT (extensión + rechazo → reversión) y murió (Sharpe activo -0.067
vs listón 0.961). H009 prueba la CARA OPUESTA de la misma teoría de subasta: ACEPTACIÓN fuera del
VA → continuación (momentum). NO es caza de variantes — es el mecanismo económico INVERSO. Se
pre-registra el FALSADOR ANTES de correr nada, para CERRAR la última cara abierta de la familia AMT.
No es una reapertura del programa: usa datos ya descargados, no toca holdout, probabilidad previa BAJA.

## What Changes

SOLO LA FICHA. Cero código, cero corridas, cero acceso a datos.

- **`hypotheses/H009_amt_continuation.yaml`** (esquema de H008), con todo fijado AHORA:
  justificación (mecanismo inverso, no variante) + nota de literatura (el cribado 2026-08-29 no
  halló validación empírica rigurosa de AMT → SIN bruto reportado creíble, debilidad estructural
  registrada); contexto de DESEQUILIBRIO ((high−low)/ATR14 > 1.5, zona 1.0-1.5 excluida de ambas),
  aceptación K=3 (mismo K que el rechazo de H008), entrada límite en dirección de la extensión,
  geometría SIMÉTRICA (objetivo/stop = 1×rango_VA, POC ya no es objetivo); diseño incremental
  pareado; **nulo con GEOMETRÍA PRESERVADA** (verificación de sanidad ~50% objetivo) — la lección de
  H008; suelo de costes (duty ~0.15 < H008, listón activo ~1.28); poder (T ~60-120 → riesgo
  UNDERPOWERED declarado); expectativa derivada de lo propio (Sharpe activo −0.3..+0.3, MUERTA o
  UNDERPOWERED, prob. previa BAJA); FALSADOR de 3 condiciones congelado; robustez única contada
  (bucket $5, deflated Sharpe N=2); sensibilidad de fills obligatoria; holdout corte 2024-03-01.
- **`hypotheses/QUEUE.md`:** H009 como PRE_REGISTRADO + nota de que es un test de cierre, no una
  reapertura ni un candidato viable.

## Impact

- NUEVO: `hypotheses/H009_amt_continuation.yaml`. MOD: `hypotheses/QUEUE.md`.
- Sin código, sin corridas, sin datos, holdout intacto. La ficha se revisa antes de implementar.
