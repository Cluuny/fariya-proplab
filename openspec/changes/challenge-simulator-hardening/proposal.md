## Why

Un tercer review corrió el simulador y encontró que la capa económica **provisional** sigue mal especificada y trajo una perilla nueva. Nada de esto rompe el veredicto de H001 (que usa Sharpe, invariante al apalancamiento), pero son deudas de honestidad que conviene saldar antes de seguir: un número sesgado sin bandera, una perilla oculta, y una afirmación de spec que no tiene test. La regla del proyecto aplica: si un parámetro de modelado determina el resultado, no es un resultado. La corrección más limpia es **retirar el valor provisional mal especificado** en vez de maquillarlo, y dejar sólo las primitivas honestas hasta construir el objetivo real (sem 9-10).

## What Changes

Correcciones puntuales en `src/challenge.py` (todas confirmadas a nivel de línea):

- **`expected_days` sesgado sin bandera.** Sólo se pone `nan` cuando `p_cond<=0`, NO cuando `insufficient_horizon`. A 0.25× con `p_unresolved=0.979` reporta ~1147 días, condicionado al ~2% más rápido que sí absorbió. → `expected_days_to_pass` SHALL ser `nan` cuando `insufficient_horizon`, igual que el valor.
- **Perilla oculta nueva** en `_economic_value`: `s = min(p_survive_cycle, 0.9995); expected_payouts = s/(1-s)`. A bajo apalancamiento `s→1`, el cap fija ~1999 ciclos (~166 años): la respuesta la determina el `0.9995`, no los datos. Es `daily_capital_cost` con otro nombre. → **Retirar por completo** el cálculo del valor por año provisional (además mal especificado: su óptimo cae en el borde 3.0× por asumir reingreso ilimitado a $500 la cuota) y el cap. Se reportan sólo las **primitivas honestas**: curva de P condicional a absorción y `P(quemar)`. Se conserva `p_burn` (correcto: sube con el apalancamiento) y la fase fondeada que lo produce. `optimal_leverage` sigue `None`; `leverage_value_curve` queda vacía.
- **Docstring de cabecera incorrecto** (línea 17): "P(pass) vs leverage curve → optimal multiplier" — la línea de §3.4 que ya acordamos incorrecta. → corregir para reflejar curvas diagnósticas y `optimal_leverage` diferido.
- **Suposición sin documentar** en `_funded_phase`: asume que el balance no se resetea tras el payout, pero los brokers reales SÍ resetean al balance inicial. → documentar la limitación en el docstring (sin cambiar comportamiento).
- **Invariante de borde sin test** (vacío por construcción con `optimal_leverage = None`). → anotar en el spec que su test es tarea de la sem 9-10, no algo cerrado.

Y como **nota de diseño para la sem 9-10** (sólo texto, NO implementación): el objetivo de decisión correcto es un problema de **umbral** alineado con §1.2 — `maximizar P(ingreso mensual ≥ $2500 sostenido durante 24 meses)` — un problema de barrera con óptimo interior natural (apalancar de más falla por quema; de menos, por payouts insuficientes), que además hace endógeno el número de cuentas a escalar (decisión sem 11). Respaldo mínimo: `max valor/año s.a. P(quemar) ≤ umbral`.

## Capabilities

### New Capabilities
<!-- Ninguna. -->

### Modified Capabilities
- `challenge-simulator`: MODIFICA "Métricas económicas del challenge" (`expected_days` nan bajo horizonte insuficiente; se retira el valor por año provisional — sólo primitivas honestas hasta el objetivo umbral) y "Curva de probabilidad frente a apalancamiento" (reportar la curva de P condicional y opcionalmente `P(quemar)`, NO una curva de valor mal especificada; el objetivo comprometido de sem 9-10 es el objetivo UMBRAL y el test del invariante de borde es tarea de esa fase).

## Impact

- **Código**: `src/challenge.py` (guard sobre `expected_days`; eliminar `_economic_value` provisional y el cap `0.9995`; docstrings de cabecera y `_funded_phase`), `src/config.py` (posible limpieza de `profit_split`/`account_capital` si sólo servían al valor retirado — evaluar; `payout_interval_days` se conserva para la fase fondeada de `p_burn`), `src/report.py` (dejar de mostrar el valor por año; mostrar `P(quemar)` y la curva de P condicional), `tests/test_challenge.py`.
- **Comportamiento observable**: `expected_net_value`/`leverage_value_curve` dejan de reportar un número (ausente en vez de equivocado); `expected_days_to_pass` es `nan` bajo horizonte insuficiente. `p_burn`, contabilidad de tres resultados, block bootstrap y verificación analítica SIN cambios.
- **Fuera de alcance**: objetivo umbral / valor endógeno (sem 9-10); Dukascopy + universo (`dukascopy-ingestion`); swap y `sum(|w|)` (`universe-and-costs`).
