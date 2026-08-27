# Cierre formal del programa

## Why

El cribado de amplitud (`docs/terrain_breadth.md`) cerró el programa de raíz: ningún terreno
accesible tiene el N_eff para despejar el listón. Falta formalizar el cierre para que quede
autosuficiente dentro de un año, con una relectura honesta (una restricción, nueve veces) y una
puerta de reapertura con condiciones OBJETIVAS, no corazonadas.

## What Changes

1. **`docs/program_verdict.md` — versión FINAL, autosuficiente:** marcado como cierre formal;
   añadida la **RELECTURA (§1.8)**: al menos 5 de las 9 murieron por AMPLITUD, no por lo que
   creímos entonces (H001 N_eff 3.73, H007 5.32, H002 3.41, sectorial 1.29, H008 ~1.1, order flow
   + coste) → una restricción estructural manifestándose nueve veces. Ya contenía las 9 familias,
   las conclusiones medidas (1.2), §1.7 amplitud, los hallazgos propios (ĉ 2.5-3.0, TI no
   subsumido, perfil no redundante 26%, N_eff cripto 2.16), la validación externa (1.6,
   arxiv:2608.21888) y los caveats (0.40 neto, IC demostrados).
2. **`hypotheses/QUEUE.md` — estado final:** banner de PROGRAMA CERRADO, cola vacía de viables,
   resultado de las corridas 001-003 del pipeline, lenguaje «sigue viva en cola» corregido.
3. **`README.md` — resumen de diez líneas** para quien llega de fuera: qué es, qué midió, qué
   concluyó, cómo reproducirlo.
4. **Tag de versión final en git** (`v1.0-closed`).
5. **`docs/reopening_conditions.md` — lo único que deja la puerta abierta:** tres condiciones
   objetivas (N_eff medido ≥ 14; objetivo revisado a la baja aceptado explícitamente; IC ≥ 0.10
   medido out-of-sample), cada reapertura debe citar cuál con el número.

## Impact

- MOD: `docs/program_verdict.md` (§1.8 + cierre formal), `hypotheses/QUEUE.md`, `README.md`.
- NUEVO: `docs/reopening_conditions.md`.
- Tag git `v1.0-closed`.
- Sólo documentación (sin cambios de código); holdout intacto; sin pre-registro.
