## Why

El simulador de barrera (`challenge.py`, Bloque B) tiene un bug silencioso y peligroso: pliega el resultado "SIN ABSORBER" (la trayectoria llegó al horizonte sin tocar ninguna barrera) dentro de "FALLÓ". Como la curva de apalancamiento usa un horizonte corto (252 días), a bajo leverage las trayectorias de baja volatilidad no alcanzan el objetivo a tiempo y se cuentan como fracaso, hundiendo `P(pasar)` hacia cero en el extremo de bajo apalancamiento.

Esto **invierte la tesis central del proyecto** (documento maestro §2.1/§2.2: menos volatilidad → más `P`; con σ→0 y Sharpe fijo, `P`→1). El simulador recomienda sistemáticamente *más* apalancamiento, lo contrario de la verdad. No crashea, no falla ningún test: silenciosamente invierte la conclusión que justifica todo el sistema. Es el bug más peligroso del proyecto y debe corregirse antes de correr cualquier estrategia real.

## What Changes

- **Contabilidad de tres resultados** en `_first_passage` / `simulate_challenge`: cada trayectoria se clasifica en **PASÓ** | **FALLÓ** (tocó `-max_drawdown` o `-daily_loss_limit`) | **SIN ABSORBER** (llegó al horizonte sin tocar barrera). Nunca se pliega "sin absorber" en "falló". Se reporta `P(pasar)`, `P(fallar)` y `P(sin_absorber)` por separado, con el horizonte explícito.
- **Horizonte largo por defecto**: como FTMO eliminó el límite de tiempo, `horizon_days` sube a 3+ años (~756 días) para que `P(sin_absorber)` sea pequeño; aun así se reporta. La métrica principal es `P(pasar)` junto a días esperados hasta pasar.
- **Objetivo del optimizador de leverage corregido**: `optimal_leverage` maximiza `expected_net_value` (que pone precio al tiempo y al capital inmovilizado del bajo apalancamiento), NO `argmax(P(pasar))`. La curva `P(pasar)` vs leverage se sigue reportando (ahora monótona decreciente en leverage), pero la **decisión** de leverage sale del valor económico.
- **Métricas económicas recalculadas** sobre la contabilidad corregida, para que `expected_attempts = 1/p_both`, `expected_net_value` y `p_burn_before_payout` no queden inflados/deprimidos por truncación.
- **Comentario en `config.py`**: el P&L aditivo es correcto para sizing estático; anotar que con sizing compuesto sobre cuenta fondeada y regla trailing, el espacio-log vuelve a importar (no se arregla ahora).

## Capabilities

### New Capabilities
<!-- Ninguna capability nueva. -->

### Modified Capabilities
- `challenge-simulator`: Se AÑADE la contabilidad de tres resultados (PASÓ/FALLÓ/SIN ABSORBER separados, horizonte explícito, prohibido plegar sin-absorber en fallo) y se MODIFICA la requirement de la curva de apalancamiento para que el óptimo de decisión salga del valor esperado neto y la curva `P(pasar)` sea monótona decreciente en leverage con horizonte honesto.

## Impact

- **Código**: `src/challenge.py` (contabilidad, optimizador, métricas económicas), `src/config.py` (`horizon_days` a ~756 + comentario sobre compounding/trailing), `tests/test_challenge.py` (regresión + monotonía), posible ajuste menor en `src/report.py` para mostrar `P(sin_absorber)`.
- **Comportamiento observable**: `ChallengeResult` gana campos (`p_fail`, `p_unresolved`, `horizon_days`); `optimal_leverage` cambia de criterio; la curva de leverage cambia de forma (monótona en vez de pico interior falso).
- **Verificación**: se mantiene el test contra la fórmula cerrada (deriva cero → `P≈0.5`); se añade regresión anti-plegado y test de monotonía de la curva.
- **Costo computacional**: horizonte más largo (~3×) sube el tiempo de simulación; se mitiga con `n_bootstraps` ajustable en tests.
- **Fuera de alcance**: datos reales de Dukascopy (bloqueado en el usuario), pre-registro H001 (otro change), estrategias reales.
