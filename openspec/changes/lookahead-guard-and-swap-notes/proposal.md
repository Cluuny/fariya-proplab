## Why

Últimas correcciones del reviewer antes del pre-registro de H001. La única que es **prerrequisito duro** es un **test de look-ahead**: el equivalente, para la capa de señales, del test contra la fórmula cerrada del simulador. Con 9 instrumentos en 3 calendarios distintos, el look-ahead es la trampa que se cobra los backtests, y el test debe existir **antes** de tener una hipótesis con un resultado que guste. Además: cerrar el hito 2 (el anclaje y los datos no cubrían la misma ventana), corregir un comentario del swap equivocado por 10×, y anotar en el spec que el swap sin dirección es un bloqueante de H002.

## What Changes

- **Test de look-ahead (prerrequisito).** `test_lookahead_guard`: una señal que mira el futuro (peso = signo del retorno de mañana) debe dar Sharpe absurdamente alto; una que sólo mira el pasado, modesto. Si el primero no explota, la convención de `shift` está rota en la dirección que oculta el bug; si el segundo explota, hay look-ahead. Verifica la convención `w_{t-1}·ret_t` del motor de extremo a extremo.
- **Hito 2 → verde.** El anclaje externo (0.74) usaba la ventana 2010-2025; los datos empiezan 2011-09-19. Recomputado sobre la ventana **exacta** (2011-09-19 → 2026-08-14): el nivel inicial del SPX500 es **1204.1**, que coincide con el cierre público real del S&P 500 ese día (verificación externa: el CFD de Dukascopy ES el índice). CAGR 13.3%, vol 16.9% → Sharpe ≈ 0.80. `SHARPE_REFERENCE` se recomputa a la ventana correcta y el motor lo reproduce; el hito pasa a verde.
- **Comentario del swap corregido.** `swap: float = 0.00003` son **0.3 bp/día**, no "~3 bp" como decía el comentario (error de 10×). La magnitud es correcta (~1% anual de diferencial ≈ 0.27 bp/día); se corrige el comentario para no calibrarlo 10× arriba en el futuro.
- **Swap sin dirección = bloqueante de H002 (anotado, no arreglado).** El swap es siempre un cargo positivo sobre `|w|`. Para H001 (trend) es una aproximación conservadora aceptable (siempre resta, errar hacia abajo es seguro). Para H002 (carry) el swap ES el retorno de la estrategia: largo AUDUSD históricamente cobraba. Con este modelo H002 es estructuralmente incapaz de ganar. Se anota en el spec como bloqueante de H002; NO se arregla ahora.

## Capabilities

### Modified Capabilities
- `backtest-engine`: AÑADE el requisito de ausencia de look-ahead (convención de shift verificable), y MODIFICA el requisito de costos para documentar que el swap no tiene dirección (aproximación conservadora; bloqueante de H002/carry).

## Impact

- **Código**: `tests/test_lookahead.py` (nuevo), `src/config.py` (comentario del swap; `SHARPE_REFERENCE` recomputado), `tests/test_real_data.py` (referencia actualizada), reporte HTML (hito 2 verde).
- **Comportamiento**: sin cambios de comportamiento del motor; el swap sigue igual (sólo se documenta su limitación de dirección). `SHARPE_REFERENCE` cambia de valor/ventana.
- **Fuera de alcance**: darle dirección al swap (bloqueante de H002, se hará cuando se proponga H002); el pre-registro de H001 (va inmediatamente después de este change).
