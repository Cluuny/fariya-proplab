# Plan del mes de Norgate v2 — un test que SÍ discrimina + deadline duro

## Por qué

El plan v1 (`docs/futures_month_plan.md`) está bien escrito pero su test principal **no
puede discriminar**. El criterio de nivel (bruto de futuros vs 0.42) tiene un IC tan ancho
que su resultado se conoce de antemano:

    0.370 ± 1.96 × 0.240 = [−0.10, +0.84]

Para no cruzar 0.42 haría falta un bruto medido ~0.85+ o ~0.0 — ambos improbables. El
resultado INDETERMINADO no es "probable": es **~seguro por construcción del test**. Un test
cuyo veredicto se sabe de antemano no justifica el gasto por sí solo.

## Qué cambia

Actualiza `docs/futures_month_plan.md`:

- **(A)** Documenta explícitamente que el test de nivel no puede discriminar (indeterminado
  por construcción).
- **(B)** Añade el número **1b — Δ bruto contra nuestro propio CFD** sobre la ventana común
  exacta. Los portafolios comparten FX y metales (ρ ~0.75) → SE de la diferencia colapsa a
  ~0.17 (vs 0.24 del nivel), por bootstrap **pareado** por bloques. Responde la pregunta
  económica real: ¿rates + energía + HG suben el bruto de trend de forma medible? Criterio
  comprometido: Δ > +0.15 → aportan (GO); Δ ≈ 0 → opción A muerta por evidencia propia; IC
  cruza 0 → no concluyente. Expectativa comprometida: Δ +0.05 a +0.20, IC probablemente
  cruza 0 pero mucho más estrecho. Reordena (2.3): **1b primero (decide)**, luego 1 (nivel,
  indeterminado), luego 2 (N_eff), luego 3 (roll).
- **(C)** Endurece el deadline (2.6): **cancelar el DÍA 3 pase lo que pase**, salvo GO
  limpio en 1b, y ejecutar la cancelación ANTES de escribir el veredicto (decisión activa,
  no pasiva).
- **(D)** Añade el recordatorio de protocolo: `tsmom` no se toca (ni lookback, ni sizing, ni
  umbrales, ni selección post-hoc); un run, cuatro números, un veredicto.

## Impacto

- Docs only: `docs/futures_month_plan.md`. Sin código, sin datos, sin delta de spec.
- NO se contrata Norgate en este change.
