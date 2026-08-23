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
de specs). Ese número ES el duty cycle disponible:

| inst | duty @ p10/90 | duty @ p5/95 |
|---|---|---|
| EURUSD | 22.9% | 14.0% |
| GBPUSD | 25.6% | 14.7% |
| AUDUSD | 25.0% | 14.8% |
| USDJPY | 31.0% | 18.5% |
| USDCAD | 24.4% | 13.7% |
| XAUUSD | 29.1% | 17.5% |
| XAGUSD | 29.1% | 18.3% |
| SPX500 | 20.7% | 10.9% |

**CORRECCIÓN (una conclusión previa de este doc era incorrecta):** el duty bajo NO
baja el listón. El requerido de la SERIE COMPLETA baja con el duty (0.24·duty+0.40),
pero el ALCANZABLE se diluye igual sobre los días flat (`Sharpe_whole ≈
Sharpe_activo·√duty`). Lo que decide es el **Sharpe del período ACTIVO requerido**,
que **SUBE** al bajar el duty (`costs_model.sharpe_activo_requerido`):

    Sharpe_activo requerido = 0.40/√duty + 0.245
    duty 100% → 0.645 · 50% → 0.81 · 20% → 1.14 · 10% → 1.51

Con duty ~20% (p10/90), COT necesita un Sharpe activo **~1.1**, no ~0.45.

## Conclusión (corregida)

8 instrumentos con COT limpio y profundo, alineado point-in-time. **El argumento a
favor de COT NO es "duty bajo baja el listón" (falso) sino que es INFORMACIÓN
NO-DE-PRECIO**: con precios competimos contra todos; con posicionamiento, no. Ése
siempre fue el argumento fuerte. El listón real (Sharpe activo ~1.1 a duty 20%) es
ALTO — por eso hay que CRIBAR el efecto con los datos ya ingeridos antes de
pre-registrar nada (`docs/cot_diagnostic.md`). **NO se pre-registra H008** hasta ver
el Sharpe activo condicional.
