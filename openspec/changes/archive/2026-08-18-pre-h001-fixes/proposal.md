## Why

Un tercer review, verificado contra los datos reales, encontró correcciones que deben ir **antes del pre-registro de H001**. La más grave sale de los propios números: las series de FX de Dukascopy traen una **barra de domingo** (sesión parcial), así que tienen ~313 barras/año en vez de ~261. Eso contamina tres cosas a la vez — el Sharpe (anualizado con √252 sobre 313 barras → subestimado ~11%), la estimación de volatilidad (los domingos enanos deflactan la vol → sobredimensionamiento en sizing vol-inversa, el peor error para un problema de barrera absorbente), y cualquier lookback expresado en barras. Además falta el **swap** (cargo diario por mantener posición), que es de primer orden para H001 (TSMOM mantiene semanas): sin él, H001 reportaría retornos que no existen. Y el hito 2 sigue en ámbar (el Sharpe de referencia es circular).

## What Changes

- **Dropear barras de fin de semana** en `loaders`: se conservan sólo sesiones Lun-Vie. Las barras de Sábado/Domingo son sesiones parciales, no días de trading; su presencia infla el conteo de barras y deflacta la vol.
- **Anualización por serie** en `engine.sharpe`: usar las barras/año **observadas** de cada serie (no un 252 global). Los índices tras el drop tienen ~247/año y el FX ~260; un factor fijo sesga a ambos en direcciones distintas.
- **Swap en `CostModel` + `engine`**: nuevo campo `swap` = cargo **diario proporcional a |peso|** (no a turnover), aplicado por día que se mantiene la posición. Es lo que hace que una estrategia de holding largo (TSMOM) reporte retornos reales.
- **Relajar el invariante `sum(|w|) ≤ 1`** en `signal-contract` a `sum(|w|) ≤ max_gross` (configurable): TSMOM con sizing por vol inversa corre exposición bruta 2-4× de forma natural; forzar a 1 aplasta la vol por debajo del objetivo y rompe la comparación contra Moskowitz-Ooi-Pedersen. La exposición se controla por vol-targeting, no por un tope de 1.
- **Renombrar `contract_jump` → `session_gap`**: sobre spot FX no hay contratos; lo que se detecta es un gap de sesión (open vs cierre previo). El nombre mentía.
- **BRENT fuera del universo activo**: 2506 obs / ~168 al año, **1421 días hábiles faltantes** (~37%) — cobertura genuinamente sparse en Dukascopy, inusable. Se retira del universo de trabajo; se conserva su mapeo con nota para evaluar un símbolo de energía más denso (p. ej. WTI) más adelante.
- **Reporte honesto**: hito 2 → **ámbar** (el Sharpe de referencia es circular: se calculó de los propios datos); recomputar `SHARPE_REFERENCE` tras el fix de calendario y citar una referencia **externa price-return** del S&P (el CFD de Dukascopy no paga dividendos → comparar contra price-return, no total-return). Mostrar los 10 instrumentos y la columna de días faltantes.

## Capabilities

### Modified Capabilities
- `data-pipeline`: MODIFICA la limpieza para dropear barras de fin de semana y renombra la anomalía de salto de contrato a `session_gap` (gap de sesión, distinto del retorno close-to-close).
- `backtest-engine`: MODIFICA el cálculo de retornos para aplicar un cargo de **swap** diario proporcional a |peso|, y el Sharpe para anualizar con las barras/año observadas por serie.
- `signal-contract`: MODIFICA el invariante de exposición de `sum(|w|) ≤ 1` a `sum(|w|) ≤ max_gross` configurable.

## Impact

- **Código**: `src/loaders.py` (drop weekend, rename), `src/engine.py` (swap, anualización), `src/config.py` (`CostModel.swap`, `max_gross`, universo sin BRENT, `SHARPE_REFERENCE` recomputado), `src/signals.py` (invariante), `src/report.py` (session_gap, missing_days).
- **Datos**: re-generar `data/clean/` (parquets sin barras de domingo). Cambian los conteos y los Sharpe reportados.
- **Tests**: nuevos/ajustados para weekend-drop, anualización por serie, swap diario, invariante relajado, session_gap; `test_real_data.py` se actualiza (Sharpe recomputado, universo sin BRENT).
- **Reporte HTML**: hito 2 ámbar, 10 instrumentos + días faltantes, caveat de dividendos.
- **Fuera de alcance**: el objetivo umbral del simulador (sem 9-10); el pre-registro/implementación de H001 (va después de este change).
