## Why

El guard de look-ahead que añadimos probaba dos instrumentos sobre un único `bdate_range` — calendarios perfectamente alineados. El riesgo real es otro: con 9 instrumentos en 3 calendarios, SPX500 tiene ~203 días hábiles que EURUSD sí tiene. Al combinar el DataFrame, esas fechas entran como NaN y `engine._asset_returns` hacía `pct_change().fillna(0)`. Reproducido: cruzando un hueco, **tanto el día del hueco como el de reapertura quedan en 0.0 — el retorno real que cruza el hueco se pierde en silencio**. Y si en vez de dropear se rellenara hacia adelante, se mantendría posición un día no cotizado y el retorno de reapertura se atribuiría al día equivocado (look-ahead sutil). El test sintético actual no puede verlo porque no hay desalineación.

## What Changes

- **`engine._asset_returns` es seguro ante huecos de calendario**: se hace `ffill` del **precio** por columna antes de `pct_change`. Así el día no cotizado da retorno **0** (una posición mantenida se mantiene, sin movimiento) y el retorno de reapertura se atribuye al **día de reapertura** — sin dropearlo (como hacía el `fillna(0)`) ni adelantarlo al día equivocado (look-ahead). Los NaN iniciales (antes de que el instrumento exista) siguen en NaN→0 (no hay posición ahí de todos modos).
- **El guard de look-ahead prueba calendarios DESALINEADOS**: la señal sintética se construye con instrumentos en calendarios distintos (uno con ~15% de días faltantes), para que el test vea la trampa que un `bdate_range` alineado ocultaba. Se añade un test que verifica que el retorno que cruza un hueco no se pierde y se atribuye a la reapertura.
- **Procedencia del anclaje de Sharpe**: el `source` de `SHARPE_REFERENCE` afirmaba un cierre público (~1204.09) sin citar de dónde. Se corrige para citar la corroboración (Wikipedia "Closing milestones of the S&P 500": índice ~1200 a mediados de sep-2011, <1100 para el 2011-10-04) con fecha de consulta, y se anota honestamente que **no se logró un cierre diario preciso de fuente independiente en sesión** (Stooq CSV vacío, FRED solo 10 años) — pendiente registrar un cierre Stooq/Yahoo con su fecha para cerrar del todo la verificación externa.
- **Política de holdout explícita (§3.5)**: el holdout sagrado (últimos 3 años apartados) no estaba documentado y se iba a correr la primera hipótesis sobre la muestra completa. Se añade `hypotheses/HOLDOUT.md` y `config.HOLDOUT_START`: H001 queda **exenta explícitamente** (test de calibración contra un paper de 1965-2009 → todo nuestro período es OOS respecto al paper; sin tuneo sobre nuestros datos), y el holdout **rige desde la primera hipótesis de descubrimiento/optimización** (H002 en adelante salvo exención). Decisión escrita, no omitida.

## Capabilities

### Modified Capabilities
- `backtest-engine`: MODIFICA el requisito de ausencia de look-ahead para exigir que el cálculo de retornos sea **seguro ante huecos de calendario** (no dropear ni adelantar el retorno que cruza un hueco cuando los instrumentos tienen calendarios distintos).

## Impact

- **Código**: `src/engine.py` (`_asset_returns` con `ffill`), `tests/test_lookahead.py` (calendarios desalineados + test de cruce de hueco).
- **Comportamiento**: cambia sólo para DataFrames con NaN por calendarios distintos (el caso multi-instrumento / portafolio, Bloque D). El backtest de un solo instrumento (su propio calendario, sin huecos internos) no cambia — el hito 2 (SPX500) se mantiene.
- **Por qué ahora**: se arregla antes de H001/portafolio, donde el DataFrame combinado de 9 instrumentos activaría el bug.
