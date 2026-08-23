## Why

`CostModel.swap` cobraba 0.3 bp/día sobre `|peso|` en AMBOS lados. En una cartera long/short eso es incorrecto, no conservador: el swap real es el diferencial de tasas, que se COBRA en unas posiciones y se PAGA en otras y se cancela parcialmente; lo que no se cancela es el margen del broker, unidireccional. Ese parámetro dictó el veredicto de tres hipótesis seguidas — es el camino crítico del proyecto, no solo un prerrequisito de H002.

## What Changes

- **`CostModel` direccional**: se separa `carry` (diferencial de tasas CON SIGNO, la larga gana `+carry`) de `swap_margin` (margen del broker, siempre costo sobre `|peso|`). El motor aplica `swap_cost = swap_margin·|w_prev| − carry·w_prev`.
- **Calibración con datos reales publicados, documentada (fuente + fecha), NO inventada** (`config` SWAP_CALIBRATION):
  - `carry` desde tasas de política publicadas (UniRateAPI, consultado 2026-08-22): Fed 4.50, ECB 2.50, BoE 4.50, BoJ 0.50, RBA 4.10, BoC 2.75, SNB 0.25, HKD→USD. `carry ≈ (r_base − r_quote)/360`; cruces aditivos; índices `(div − financing)/360`; metales `−financing/360`.
  - `swap_margin` desde la tabla long/short publicada de un broker (afterprime.com/swaps, 2026-08-23; validado contra el ejemplo de FTMO). ~0.30 bp/día (metales ~0.45), escalable con `BROKER_MARGIN_MULT`.
- **Tests**: una larga en carry positivo RECIBE swap; el margen siempre resta; una cartera que cosecha carry cuesta menos que el modelo unsigned.
- Renombrado `CostModel.swap → swap_margin`; runners de hipótesis muertas actualizados (mantienen carry=0 → reproducen sus veredictos).

## Hallazgo (validación en datos reales)

El modelo direccional **NO rescata las hipótesis de trend**: H007-A pasa de 0.184 (unsigned) a **0.182** (direccional); B de 0.040 a 0.024. Refuta la hipótesis de que el drag estaba sobrestimado 2-3×: **el margen (~0.30-0.45 bp/día, confirmado por DOS brokers reales) es real y unidireccional**, y para un libro de TREND el carry con signo se cancela (las posiciones de trend no cosechan carry sistemáticamente). El modelo es **más correcto** (y **desbloquea H002/carry**, donde el diferencial con signo ES el retorno), pero el drag de trend era real, no un artefacto del unsigned.

## Capabilities

### Modified Capabilities
- `backtest-engine`: el swap pasa a direccional (carry con signo + margen unidireccional), calibrado contra fuentes reales.

## Impact

- **Código**: `src/config.py` (CostModel direccional + calibración), `src/engine.py` (aplicación direccional), `tests/test_engine.py` (+3 tests, renombres). Runners actualizados.
- **Desbloquea H002 (carry)**: el diferencial con signo ahora es representable.
- **No cambia los veredictos de trend** (H001/H003/H007 siguen muertas); el drag era real.
