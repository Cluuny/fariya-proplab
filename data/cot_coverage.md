# COT — cobertura, mapeo y duty cycle disponible (Bloque 2)

Primera fuente de señal **NO-de-precio** del proyecto. COT = posicionamiento (CFTC
Commitments of Traders, semanal). Mecanismo (filtro 4): los comerciales cubren, los
especuladores toman el otro lado, y el desequilibrio extremo se revierte. Reproducir:
`uv run python scripts/cot_diagnostic.py`. Descarga: API pública CFTC
(`publicreporting.cftc.gov`, dataset Legacy Futures-Only `6dca-aqww`), consultado
2026-08-23 → `data/cot/<INSTRUMENTO>.csv`.

## Elección de formato: Legacy (no Disaggregated)

**Legacy Futures-Only** — split limpio comerciales (hedgers) vs no-comerciales
(especuladores grandes), la variable exacta del mecanismo, y la historia MÁS larga
(metales desde 1986). El **Disaggregated** (Producer/Swap/Managed Money/Other) es más
granular pero se introdujo en 2009 (cambio de metodología que rompe la serie). Para
"specs vs commercials" Legacy es más limpio y largo.

## Mapeo contrato CFTC ↔ instrumento (con signo)

Solo hay COT para instrumentos con futuro listado en EE.UU. De nuestros 17, aplica a
**8**. Los futuros FX se cotizan divisa-extranjera/USD, así que para pares USD-base
(USDJPY, USDCAD) el neto de specs se INVIERTE (largo yen-futuro = corto USDJPY). Si
falta un mapeo, `cot.load_cot` falla visiblemente (`CotNotMappedError`), como
`DUKASCOPY_SYMBOLS`.

| Instrumento | Contrato CFTC | signo | nota |
|---|---|---|---|
| EURUSD | EURO FX (CME) | +1 | |
| GBPUSD | BRITISH POUND (código 096742) | +1 | |
| AUDUSD | AUSTRALIAN DOLLAR (CME) | +1 | |
| USDJPY | JAPANESE YEN (CME) | **−1** | largo yen-futuro = corto USDJPY |
| USDCAD | CANADIAN DOLLAR (CME) | **−1** | largo CAD-futuro = corto USDCAD |
| XAUUSD | GOLD (COMEX) | +1 | |
| XAGUSD | SILVER (COMEX) | +1 | |
| SPX500 | E-MINI S&P 500 (código 13874A) | +1 | |

Los 9 restantes (cruces FX, GER40, JPN225, HK50) **no tienen COT** (sin futuro US) →
fuera de esta fuente.

## Alineación POINT-IN-TIME (donde vive el look-ahead)

El reporte tiene **fecha de datos = martes** y se **publica el viernes siguiente**
(~3 días de rezago). Una señal sólo puede usar el dato desde su fecha de PUBLICACIÓN.
`src/cot.py` indexa por fecha de publicación (martes + 3 días) y `align_to_prices`
hace asof: cada día de precio ve el último reporte YA PUBLICADO. Test dedicado
(`test_cot.py::test_point_in_time_no_lookahead`): un reporte con fecha de datos el
martes NO aparece hasta el viernes.

## Reporte de calidad (criterio de Brent: KILL >25% faltante)

| inst | desde | hasta | semanas | falta% (era 2000+) | AC(1) | cobertura |
|---|---|---|---|---|---|---|
| EURUSD | 2000-08 | 2026-08 | 1356 | 0.0 | 0.98 | PASS |
| GBPUSD | 1988-04 | 2026-08 | 1876 | 0.0 | 0.91 | PASS |
| AUDUSD | 2004-01 | 2026-08 | 1180 | 0.1 | 0.98 | PASS |
| USDJPY | 2000-08 | 2026-08 | 1356 | 0.0 | 0.96 | PASS |
| USDCAD | 2000-08 | 2026-08 | 1356 | 0.0 | 0.97 | PASS |
| XAUUSD | 1986-01 | 2026-08 | 1930 | 0.0 | 0.98 | PASS |
| XAGUSD | 1986-01 | 2026-08 | 1930 | 0.0 | 0.94 | PASS |
| SPX500 | 1997-09 | 2026-08 | 1505 | 0.0 | 0.85 | PASS |

**Los 8 pasan** (0-0.1% faltante en la era semanal moderna). Notas de metodología:
metales tienen data desde 1986 pero en frecuencia mensual/bisemanal hasta ~1992-2000
(por eso se mide el faltante sobre la era semanal 2000+, donde es ~0). El paso a
weekly y la introducción del Disaggregated (2009) no afectan la serie Legacy usada.
La **alta autocorrelación (0.85-0.98)** dice que el posicionamiento es MUY persistente
→ los extremos ocurren en episodios que duran semanas (bueno para una señal que
mantiene).

## Diagnóstico previo — duty cycle disponible (sin pre-registrar nada)

Fracción del tiempo en extremos de posicionamiento (percentil rodante 3 años del neto
de specs). Ese número ES el duty cycle disponible, y fija el gross requerido:

| inst | duty @ p10/90 | duty @ p5/95 | gross requerido (@p10/90) |
|---|---|---|---|
| EURUSD | 22.9% | 14.0% | 0.45 |
| GBPUSD | 25.6% | 14.7% | 0.46 |
| AUDUSD | 25.0% | 14.8% | 0.46 |
| USDJPY | 31.0% | 18.5% | 0.47 |
| USDCAD | 24.4% | 13.7% | 0.46 |
| XAUUSD | 29.1% | 17.5% | 0.47 |
| XAGUSD | 29.1% | 18.3% | 0.47 |
| SPX500 | 20.7% | 10.9% | 0.45 |

**El duty cycle disponible es ~20-30% (p10/90) o ~11-18% (p5/95)** → gross requerido
**~0.42-0.47**, frente a **0.64** de una estrategia price-based always-in. Ésa es la
razón estructural para explorar COT: **baja el listón de coste ~0.20 de Sharpe** al
operar sólo en extremos.

## Conclusión

8 instrumentos con COT limpio y profundo, alineado point-in-time, con un duty cycle
natural de ~20% → gross requerido ~0.45. Es la primera fuente que puede pasar el
filtro #6 con un edge realista (a diferencia de las tres price-based que murieron a
0.64). **NO se pre-registra H008 todavía**: la ficha se escribe con estos números de
cobertura y duty cycle a la vista, y debe estimar su gross esperado contra el ~0.45
requerido.
