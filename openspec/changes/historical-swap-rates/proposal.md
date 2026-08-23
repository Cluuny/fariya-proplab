## Why

El swap direccional (change previo) tenía un bloqueante y un bug de convención:

- **(A) BLOQUEANTE — tasas de 2026 sobre 2005-2023.** El `carry` usaba un snapshot de marzo 2026 aplicado a todo el backtest. Las tasas reales fueron muy distintas y el SIGNO se invierte en parte de la muestra: EURUSD carry real fue POSITIVO en 2009-2015 (EUR>USD), NEGATIVO en 2006-2007 y 2022-2026. Peor con USDJPY: el snapshot le acredita +4%/año a toda la muestra cuando en 2009-2015 el diferencial real era ~0.15% — carry fantasma con información del presente aplicado retroactivamente a 20 años.
- **(B) BUG DE CONVENCIÓN 360 vs 261.** La tabla anualizaba con /360 pero el motor cobra sólo en ~261 días de cotización → subestimaba carry y margen ~29%. En la realidad el broker reparte 365 días en ~261 sesiones (swap triple del miércoles).

## What Changes

- **(A) Carry HISTÓRICO** (`src/rates.py`): series mensuales de tasas de política de **BIS (WS_CBPOL), 2003-2026**, descargadas a `data/rates/policy_rates.csv` (stats.bis.org/api/v1, consultado 2026-08-22), reindexadas a diario. `carry` pasa de vector a **matriz fecha×instrumento**. Cruces aditivos; índices `(div−financing)`; metales `−financing`. Div yields de índices constantes (simplificación documentada, 2º orden). `engine.backtest` acepta `carry_matrix`.
- **(B) Factor de convención 365/261 ≈ 1.40** en AMBOS componentes (carry y margen). Consecuencia registrada: **margen efectivo 0.30 → 0.42 bp/día** — el modelo corregido es MÁS punitivo en margen que el placeholder unsigned (0.30) que mató a H001/H007, no menos.
- **(C) Validación cruzada** en el source: carry implícito del broker `(long−short)/2` vs tasas — EURUSD −0.46 vs −0.556 bp/d, XAUUSD −1.15 vs −1.25 — dos fuentes dentro del 10%, con fechas.
- **(D) `BROKER_MARGIN_MULT`** con sensibilidad {1.0, 1.5} (prop firms cobran peor que retail).
- **TEST OBLIGATORIO**: EURUSD carry POSITIVO en algún punto de 2009-2015 (si sale negativo en todo el histórico, las series no se aplican). Pasa (2011-06 = +0.437 bp/d vs 2006-06 = −0.971).

## Capabilities

### Modified Capabilities
- `backtest-engine`: el `carry` del swap pasa a histórico (matriz fecha×instrumento) con factor de convención 365/261.

## Impact

- **Código**: `src/rates.py` (nuevo), `src/config.py` (calibración histórica + factor + DATA_RATES), `src/engine.py` (`carry_matrix`), `tests/test_rates.py` (+4). **Datos**: `data/rates/policy_rates.csv` (BIS, committeado como referencia reproducible). 90 tests pasan.
- Habilita el Bloque 3 (sensibilidad retroactiva) con el modelo corregido.
