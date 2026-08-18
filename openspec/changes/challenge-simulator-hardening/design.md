## Context

Ver `proposal.md` — Why. Todo confirmado a nivel de línea en `src/challenge.py` (main): `expected_days` se pone `nan` sólo si `p_cond<=0` (no bajo `insufficient_horizon`); `_economic_value` usa `s = min(p_survive_cycle, 0.9995); expected_payouts = s/(1-s)`; el docstring de cabecera aún afirma "optimal multiplier"; `_funded_phase` no documenta la suposición de no-reset del balance. El valor por año provisional está mal especificado (óptimo en el borde 3.0×) por asumir reingreso ilimitado a la cuota.

## Goals / Non-Goals

**Goals:**
- Retirar el valor provisional mal especificado y el cap `0.9995` (perilla oculta).
- `expected_days_to_pass = nan` bajo horizonte insuficiente.
- Corregir docstrings (cabecera §3.4; suposición de `_funded_phase`).
- Dejar en el spec que el invariante de borde es tarea de sem 9-10 y documentar el objetivo umbral comprometido.
- Conservar intactos: block bootstrap, contabilidad de tres resultados, `p_burn`, verificación analítica.

**Non-Goals:**
- Construir el objetivo umbral / valor endógeno (sem 9-10 con el portafolio).
- Dukascopy + universo (`dukascopy-ingestion`); swap y `sum(|w|)` (`universe-and-costs`).

## Decisions

### D1 — Retirar el valor provisional en vez de maquillarlo
Se elimina `_economic_value` (y el cap `0.9995`). `expected_net_value` y `leverage_value_curve` dejan de reportar un número: un valor ausente es mejor que uno mal especificado con una perilla latente. Se conservan `_funded_phase` y `p_survive_cycle` porque `p_burn` (correcto) los necesita. `ChallengeResult.expected_net_value` queda como `nan` (o se retira el campo); `leverage_value_curve` queda vacía. **Alternativa:** dejar el valor con caveats — rechazada: el reviewer mostró que la perilla `0.9995` determina el régimen de bajo apalancamiento y el óptimo cae en el borde; caveatear un número equivocado no lo arregla.

### D2 — `expected_days` honesto bajo el guard
`expected_days_to_pass = nan` cuando `insufficient_horizon` (hoy reporta ~1147 días condicionado al ~2% que absorbió). Mismo criterio que el valor. **Alternativa:** reportarlo con bandera — el número sigue siendo sesgado; `nan` es más honesto.

### D3 — Docstrings
Cabecera de `challenge.py`: quitar "P(pass) vs leverage curve → optimal multiplier"; reflejar que se reportan curvas diagnósticas y `optimal_leverage` está diferido al objetivo umbral. `_funded_phase`: documentar que el modelo NO resetea el balance tras el payout mientras los brokers reales SÍ lo hacen (limitación conocida; no se cambia el comportamiento ahora).

### D4 — Config: evaluar qué parámetros quedan huérfanos
Si `profit_split`/`account_capital` sólo servían al valor retirado, se eliminan de `FirmRules` para no dejar perillas muertas. `payout_interval_days` (y `n_payouts`) se conservan porque la fase fondeada de `p_burn` los usa. Se decide en implementación revisando referencias.

### D5 — El objetivo umbral queda como decisión de diseño, no como código
Se documenta en el spec (y aquí) el objetivo comprometido de sem 9-10: `maximizar P(ingreso mensual ≥ $2500 sostenido 24 meses)` — un problema de barrera con óptimo interior natural, sin perillas, que además hace endógeno el escalado de cuentas. No se implementa en este change.

## Risks / Trade-offs

- **Consumidores de `expected_net_value`/`leverage_value_curve`** (report, tests) → Mitigación: actualizar `report.render_challenge` para no mostrar el valor y sí `P(quemar)` + curva condicional; ajustar `test_expected_net_value_monotonic_in_edge` (se retira o se reconvierte a un test de `p_burn`/condicional) y `test_report_integration`.
- **Campo `expected_net_value` retirado vs. dejado como nan** → dejarlo como `nan` es menos disruptivo para consumidores; se decide en implementación. En cualquier caso deja de ser un número calculado.

## Open Questions

- ¿Eliminar el campo `expected_net_value` de `ChallengeResult` o dejarlo fijo en `nan`? Diferible; no cambia el contrato observable (no hay número). Se decide al implementar según los consumidores.
