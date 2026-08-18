## Context

Ver `proposal.md`. Implementa la señal TSMOM contra el contrato congelado en `hypotheses/H001_tsmom.yaml` y corre el primer veredicto. El motor (`engine.backtest`, `rolling_vol`, `sharpe`, `_asset_returns` gap-safe) y los datos limpios ya existen.

## Decisions

### D1 — `tsmom(prices, *, lookback_months=12, vol_window=63, vol_target=0.08, max_gross=config.MAX_GROSS_EXPOSURE, rebalance='BMS')`
Función pura, sin I/O ni estado. Pasos:
1. **Retorno a 12 meses de calendario, gap-safe**: por columna, `past = precio.reindex(fecha - DateOffset(months=lookback), method='ffill')`; `ret_L = precio/past - 1`. Signo → dirección `s ∈ {-1,0,+1}` (0 donde no hay 12m de historia).
2. **Vol-inversa relativa**: `raw = s / vol`, con `vol = engine.rolling_vol(prices, vol_window)`. Normalizar a `sum(|raw|)=1` por fila (pesos relativos).
3. **Escalado ex-ante a vol de portafolio (un paso, sin iterar)**: retornos del portafolio sin escalar `rp = (raw.shift(1) * _asset_returns(prices)).sum(axis=1)`; `vol_p = rp.rolling(63).std()*sqrt(bars_per_year)`; **`.shift(1)`** para usar sólo info hasta t-1; `escalar = vol_target / vol_p`. `w_full = raw * escalar`.
4. **Cap de bruto**: si `sum(|w_full|) > max_gross` en una fecha, recortar el escalar de ESA fecha para que quede en `max_gross`.
5. **Rebalanceo mensual**: muestrear `w_full` en el primer día hábil de cada mes (`BMS`) y `ffill` al frame → holding entre rebalanceos.

Determinismo y pureza: todo es función de `prices`; no muta la entrada (opera sobre copias/derivados).

### D2 — Ex-ante verificable con un test de extensión
El escenario "añadir fechas futuras no cambia los pesos pasados" es el test que ata el ex-ante. Como `rolling().std()` sólo mira hacia atrás y hacemos `.shift(1)`, extender la serie por el futuro no toca ninguna fecha previa. El test lo verifica sobre datos reales recortados vs completos.

### D3 — Runner `scripts/run_h001.py`
- Carga `data/clean/*.parquet` (columna `close`) de los 9; construye el frame unión.
- **Muestra A**: columnas FX+oro, evaluación desde la primera fecha con señal viva ≥ 2004-01-01. **Muestra B**: los 9, evaluación desde ≥ 2015-01-01. La señal usa TODA la historia previa para lookback/vol; sólo se recorta la **ventana de evaluación** del Sharpe.
- **Especificación primaria**: swap 0.3 bp (`config.DEFAULT_COST`). **Sensibilidad**: swaps 0.0 y 1.0 bp (CostModel con swap override). Se computa Sharpe neto por (muestra × swap).
- **Veredicto por muestra** (sobre swap 0.3): ≥0.4 viable; <0.2 muerta; [0.2,0.4] → correr lookback 6m (robustez), `intentos=4`, deflated Sharpe; promueve sólo si deflated>0.4, si no parked.
- **Deflated Sharpe**: corrección Bailey-López de Prado por N intentos (aprox. con el ajuste estándar del máximo esperado de N Sharpes independientes). Se reporta el número, es criterio.
- Regla de dos muestras: si A≥0.4 y B<0.2 → hallazgo = degradación post-2010.

### D4 — Escritura del veredicto en la ficha
Tras correr, se añaden a `H001_tsmom.yaml`: `fecha_test`, `intentos_realizados`, `resultado` (Sharpe por muestra×swap), `veredicto` (por muestra + global), y `estado` final. NO se toca `FALSADOR`, `metrica_exito`, ni `resultado_esperado` (congelados). Esto es registro post-ejecución, no mover el poste.

## Risks / Trade-offs
- **`BMS` (business month start) puede caer en feriado no-hábil de un instrumento**: el `ffill` del muestreo lo resuelve (usa el último peso disponible); la ejecución la maneja el `shift(1)` del motor.
- **Muestra A con 6 instrumentos** tiene menos amplitud → su Sharpe esperado es más bajo aún; se interpreta con esa lente.
- **Deflated Sharpe es una aproximación**: se reporta la fórmula usada; su papel es no leer un 0.45-tras-2-variantes como éxito limpio.

## Open Questions
- Ninguna que bloquee. El valor exacto del cap y del vol_window son los del contrato (4 y 63); no se tunean.
