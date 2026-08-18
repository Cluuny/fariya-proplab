## Why

Un review externo corrió el simulador con una estrategia realista (Sharpe 0.8, vol 8% anual — el objetivo del propio documento) y encontró que **el motor de DECISIÓN da la respuesta contraria a la verdad**: `optimal_leverage` (por `expected_net_value`) cae en `3.0×`, el **borde del grid** — la firma de una función objetivo mal especificada. La tesis del proyecto (§2.1: menos volatilidad → más P) queda invertida.

El diagnóstico es preciso: el bug de truncación que corregimos en la *contabilidad* (change `three-outcome-accounting`) **sobrevivió mudándose a la *economía***, un nivel más abajo, donde quedó invisible porque las tres probabilidades reportadas ahora están bien. Este change corrige la capa económica/decisión antes de tocar datos reales — un motor invertido sobre datos reales produce un veredicto invertido con aire de rigor.

## What Changes

Tres bugs confirmados a nivel de código en `src/challenge.py` (main):

- **BUG 1 (crítico) — la truncación se mudó a la economía.** `expected_attempts = 1/p_both` con `p_both = p_phase1*p_phase2`, y ambas cuentan `SIN ABSORBER` como no-paso. A bajo apalancamiento el ~98% no absorbe → `p_both≈0.006` → 157 intentos → coste de tiempo ×157 → valor enorme negativo. Un intento **no termina en el horizonte; termina cuando toca una barrera** — si sigues corriendo no pagas otra cuota, sigues en el mismo intento.
- **BUG 2 — `p_burn` invertido.** `p_survive_cycle = p_phase2` (alcanzar +5%). Sobrevivir un ciclo de payout es **no tocar −10%**, no alcanzar +5%. Una trayectoria sin absorber sobrevivió pero se cuenta como quemada → `p_burn` **baja** con el apalancamiento (imposible).
- **BUG 3 — `expected_days` ignora los fallidos.** `days1[passed1].mean() + days2[passed2].mean()` promedia sólo ganadoras; los intentos que fallan también consumen días. Y `_first_passage` sólo registra `day_passed` para pasadas; las quemadas quedan en `horizon`.

Correcciones (rediseño, no calibración):

- **Probabilidad condicional a absorción**: `p_cond = p_pass/(p_pass+p_fail)` por fase; `expected_attempts = 1/(p_cond1·p_cond2)`. Es la probabilidad de primer paso correcta; la fracción sin absorber es una señal de calidad de horizonte, no un resultado.
- **Guard de horizonte insuficiente**: si `p_unresolved > 0.05` en alguna fase, **no reportar** `expected_net_value` (nan + bandera), en vez de un número engañoso.
- **`p_burn` correcto**: sobrevivir = complemento de FALLA; `p_burn` debe **subir** con el apalancamiento.
- **`expected_days` correcto**: registrar día de absorción para pasadas **y** quemadas; incluir el tiempo de los intentos fallidos.
- **Matar `daily_capital_cost`** (parámetro inventado que fija la ubicación del óptimo). `payout_per_cycle` **derivado** simulando la fase fondeada (profit split × retorno esperado | sobrevive), NO fijo: el payout escala con el retorno. Se reporta un valor por unidad de tiempo **provisional** como diagnóstico.
- **DECISIÓN (sem 6): `optimal_leverage = None`** con motivo explícito. Tras arreglar los bugs, el óptimo por valor/tiempo cae en el borde por una propiedad real (dinero de la casa, riesgo-neutral), no por artefacto; y el documento se contradice (§2.1 mínimo vs §3.4 máximo). Elegir un óptimo hoy lo fijaría una perilla, no los datos. El objetivo real (valor/tiempo con payout endógeno) se construye en **sem 9-10** con el modelo de fase fondeada del portafolio. Se reportan **ambas curvas** (P condicional y valor provisional). **Invariante:** óptimo en borde del grid = objetivo mal especificado → error. H001 (sem 8) no depende de esto (su falsador es Sharpe, invariante al apalancamiento).
- **Sin centinela mágico**: reemplazar `return -1e12` por `nan` y excluirlo del `argmax`.
- **Invariante de spec**: ninguna métrica reportada puede tratar `SIN ABSORBER` como fallo, ni directa ni indirectamente.

## Capabilities

### New Capabilities
<!-- Ninguna. -->

### Modified Capabilities
- `challenge-simulator`: AÑADE un invariante ("ninguna métrica pliega SIN ABSORBER en fallo"); MODIFICA "Métricas económicas del challenge" (P condicional a absorción, `expected_days` con intentos fallidos, `p_burn` como complemento de FALLA, `payout` derivado, objetivo valor/tiempo, guard de horizonte) y "Curva de probabilidad frente a apalancamiento" (reporta ambas curvas; `optimal_leverage = None` con la DECISIÓN de diferir el objetivo a sem 9-10 y el invariante de borde).

## Impact

- **Código**: `src/challenge.py` (`_first_passage` registra absorción de ambos resultados; economía condicional a absorción; objetivo valor/tiempo; payout derivado de fase fondeada; guard; nan), `src/config.py` (elimina `daily_capital_cost`; `payout_per_cycle` deja de ser input fijo), `tests/test_challenge.py`, y posible ajuste en `src/report.py` para la bandera de horizonte.
- **Comportamiento observable**: `optimal_leverage` cambia (ya no en el borde); `p_burn` invierte su tendencia (correcta); `expected_net_value` puede ser `nan` (horizonte insuficiente); nuevos campos/bandera en `ChallengeResult`.
- **Riesgo**: derivar el payout de la fase fondeada añade una sub-simulación; es la pieza de diseño principal.
- **Fuera de alcance** (otros changes): universo (Nikkei/Brent) + mapeo Dukascopy, swap en `CostModel`, `sum(|w|)≤1`, límite diario sobre cierres, pre-registro H001.
