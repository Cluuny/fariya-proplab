## Why

Tres consecuencias/higiene de los fixes anteriores, más una decisión que toca H001. (1) El `ffill` que arregló el P&L pone retorno **cero** en los días de hueco; eso **deflacta la vol estimada** de los índices (medido: SPX500 en el DataFrame combinado, **21%** de deflación; FX ~2%). Para el sizing por vol inversa de H001 eso **sobredimensiona índices** sistemáticamente — la misma clase de error direccional que las barras de domingo, y un problema de barrera absorbente no la perdona. (2) El anclaje de Sharpe está bien pero mal nombrado: lo externo es que el nivel coincide con el índice; el 0.80 vs 0.82 es un check entre dos estimadores, no una verificación contra un paper. (3) El reporte de avance arrastra copy por tercera vez (chips 70/10 vs KPIs 69/9) — hay que **generar los KPIs del repo**, no teclearlos (regla dura del README: reporte regenerable con un comando).

## What Changes

- **`engine.rolling_vol` — estimación de vol segura ante huecos.** Estima la vol de cada instrumento sobre **sus propios días de cotización** (descartando los ceros que el `ffill` inyecta en los huecos), anualizada con sus barras/año. Para el sizing vol-inversa de H001 se usa esto, no la vol de `_asset_returns`.
- **Anclaje: nombrar lo verificado.** `SHARPE_REFERENCE.source` reescrito: lo EXTERNO es que la serie ES el índice (nivel inicial = cierre público → su Sharpe es el del índice por construcción); el 0.80↔0.82 es un cross-check interno (geométrico vs aritmético), NO una comparación contra un paper. Pendientes anotados: verificar el endpoint FINAL (2026-08-14) y un tick independiente exacto.
- **Limitación de `ffill` documentada:** también extiende el último precio si una serie termina antes que las otras. Hoy no aplica (todas cierran ~2026-08); se anota para cuando se añada un instrumento de historia más corta.
- **KPIs del reporte generados desde el repo.** `scripts/report_kpis.py` computa tests, PRs, instrumentos, specs, changes, holdout y el Sharpe de referencia desde el repo. El reporte de avance toma sus KPIs de ahí, en vez de teclearlos.

## Capabilities

### New Capabilities
<!-- Ninguna. -->

### Modified Capabilities
- `backtest-engine`: AÑADE la estimación de volatilidad segura ante huecos (vol por días propios), MODIFICA el requisito de reproducción del Sharpe para nombrar con precisión qué es externo (el endpoint = índice) y qué es interno (acuerdo entre estimadores), y anota la limitación de `ffill` en colas.
- `reporting`: AÑADE que los KPIs del reporte de avance se derivan del repo (regenerables), no se teclean.

## Impact

- **Código**: `src/engine.py` (`rolling_vol`), `src/config.py` (`SHARPE_REFERENCE.source`), `scripts/report_kpis.py` (nuevo), `tests/test_engine.py`.
- **Comportamiento**: `rolling_vol` es una herramienta nueva (H001 la usará); no cambia backtests existentes. El P&L y el hito 2 no cambian.
- **Fuera de alcance**: implementar el sizing vol-inversa de H001 (usará `rolling_vol`); verificar los endpoints del S&P contra una fuente que no se pudo alcanzar en sesión.
