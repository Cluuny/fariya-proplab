## Why

Al correr `loaders` sobre datos reales de Dukascopy se vio que `anomalous_return` y `contract_jump` dan **el mismo conteo** por instrumento: `_detect_contract_jumps` reusa el mismo z-score sobre los mismos retornos close-to-close con el mismo umbral `>5σ` que la detección de retornos anómalos, así que **cada outlier se cuenta dos veces** bajo dos nombres. El reporte de calidad infla los conteos y "contract_jump" no aporta señal distinta. Además, ahora que el pipeline corre sobre datos reales, conviene una forma de **verificar en código** que la ingesta+limpieza produjo lo esperado.

## What Changes

- **`_detect_contract_jumps` detecta un gap overnight**, no un retorno close-to-close. Un salto por cambio de contrato/rollover se manifiesta como un **gap de apertura** (`open_t` vs `close_{t-1}`), distinto del retorno close-to-close que ya cubre `anomalous_return`. Se z-scorean los gaps y se marcan los `> σ`. Si no hay columna `open`, no se detectan (devuelve vacío) en vez de re-marcar los retornos.
- Resultado: `anomalous_return` y `contract_jump` dejan de coincidir; cada uno señala un evento distinto (movimiento intradía-a-intradía vs. hueco entre sesiones).
- **Verificación en código de los datos reales**: un test (que se salta si no hay parquets) que valida sobre `data/clean/` que están los 10 instrumentos del universo, que el buy&hold de SPX500 reproduce `SHARPE_REFERENCE` dentro de tolerancia (verificación del motor sobre datos reales = hito 2), y que el detector marca un evento conocido.

## Capabilities

### New Capabilities
<!-- Ninguna. -->

### Modified Capabilities
- `data-pipeline`: MODIFICA "Validación de calidad de datos" para que la detección de saltos por cambio de contrato sea una señal DISTINTA de los retornos anómalos (gap overnight `open` vs cierre previo), sin doble conteo del mismo evento.

## Impact

- **Código**: `src/loaders.py` (`_detect_contract_jumps` y su llamada en `validate`).
- **Tests**: `tests/test_loaders.py` (contract_jump ≠ anomalous_return sobre datos sintéticos con gap pero sin outlier close-to-close), `tests/test_real_data.py` (verificación sobre datos reales, skip si ausentes).
- **Comportamiento observable**: el reporte de calidad deja de duplicar conteos; `contract_jump` marca gaps de apertura reales (rollover). Sin cambios en las demás validaciones.
