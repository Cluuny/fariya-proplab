## Context

Ver `proposal.md`. Verificado en datos reales: EURUSD tiene 313 barras/año (Lun-Vie ~1215 c/u + **Domingo 1212**); `engine.sharpe` anualiza con `TRADING_DAYS_PER_YEAR=252`; `CostModel` no tiene swap; el invariante de `signals` es `sum(|w|)≤1`; BRENT tiene 2506 obs / 1421 días hábiles faltantes; la anomalía de gap se llama `contract_jump`.

## Goals / Non-Goals

**Goals:** calendario correcto (sin fin de semana), anualización por serie, swap diario, invariante relajado, rename `session_gap`, BRENT fuera, hito 2 ámbar con referencia recomputada + cross-check externo. Todo antes de H001.

**Non-Goals:** objetivo umbral del simulador (sem 9-10); pre-registro/implementación de H001; reemplazar BRENT por otro símbolo de energía (evaluación posterior).

## Decisions

### D1 — Dropear barras de fin de semana en `loaders.clean`
Filtrar `index.dayofweek < 5` (Lun-Vie). Estándar para daily FX: una barra diaria debe ser una sesión completa; la de domingo (2-3h) no lo es. Los retornos siguen siendo close-to-close, así que el gap de fin de semana queda capturado en el retorno Vie→Lun. **Alternativa:** mergear domingo en lunes — más complejo y sin beneficio para EOD; descartada.

### D2 — Anualización por serie en `engine.sharpe`
`sharpe(returns, periods_per_year=None)`: si `None` y el índice es datetime, inferir `periods_per_year = len / años_span`; si no, usar 252 (para arrays sintéticos sin fecha). Cada serie se anualiza con su propio calendario. **Nota:** los tests que comparan `sharpe(net)` vs `sharpe(pct_change)` siguen coincidiendo (misma anualización a ambos lados).

### D3 — Swap en `CostModel` + `engine.backtest`
Nuevo campo `CostModel.swap` = cargo diario por unidad de `|peso|` mantenido. `engine.backtest` añade `swap_cost_t = sum_i |w_{i,t-1}| · swap_i` cada día (usa el peso mantenido, no el turnover). Default placeholder documentado (~3e-5/día), calibrable por instrumento. **Por qué |peso| y no turnover:** el swap se paga por mantener, no por rotar; TSMOM rota poco pero mantiene semanas.

### D4 — Relajar `sum(|w|) ≤ 1` a `≤ max_gross`
`config.MAX_GROSS_EXPOSURE` (default p. ej. 4). `signals.validate_weights`/`check_exposure` usan `max_gross`. La exposición absoluta se controla por vol-targeting y el escalado de apalancamiento del simulador, no por el contrato de señal. **Por qué:** TSMOM vol-inversa corre bruto 2-4×; forzar a 1 aplasta la vol y rompe la comparación con el paper.

### D5 — Rename `contract_jump` → `session_gap`
Sobre spot FX no hay contratos; se detecta un gap de sesión (`open` vs cierre previo). Se renombra el tipo de anomalía y la función `_detect_contract_jumps` → `_detect_session_gaps`. `report` muestra `session_gap`.

### D6 — BRENT fuera del universo activo
`config.INSTRUMENTS` sin BRENT (37% de días hábiles faltantes = inusable). Se conserva su entrada en `DUKASCOPY_SYMBOLS`/`DUKASCOPY_POINT` con un comentario de que la cobertura diaria de Dukascopy es sparse y de evaluar un símbolo de energía más denso (p. ej. WTI `LIGHTCMDUSD`) antes de re-incluir energía. El universo activo queda: 5 FX + oro + SPX500 + GER40 + JPN225.

### D7 — `SHARPE_REFERENCE` recomputado + cross-check externo; hito 2 ámbar
Tras D1/D2, recomputar el Sharpe de SPX500 buy&hold (cambia por el calendario). Fijar `SHARPE_REFERENCE.value` al nuevo número y citar en `source` una estimación **externa price-return** del S&P 2011-2026 (el CFD Dukascopy NO paga dividendos → comparar contra price-return, no total-return). El hito 2 se mantiene **ámbar** hasta un cross-check externo riguroso; el reporte lo refleja.

### D8 — Reporte honesto
Reporte HTML: hito 2 ámbar; tabla con los **10** instrumentos + columna de **días faltantes**; caveat de dividendos. El reporte de calidad (`render_report`) ya expone `missing_days`; asegurar que se muestre.

## Risks / Trade-offs

- **Re-generar parquets cambia todos los números** (Sharpe, conteos) → esperado; `test_real_data.py` se actualiza al nuevo `SHARPE_REFERENCE` y universo sin BRENT.
- **Default del swap es un placeholder** → documentado; su valor exacto es una calibración posterior (como los costos). El contrato es que exista y escale con días × |peso|.
- **`max_gross` es un parámetro nuevo** → riesgo de que oculte sobre-apalancamiento; mitigación: el vol-targeting de H001 controla la vol real, y el simulador escala el apalancamiento explícitamente.
- **Anualización inferida** puede ser ruidosa en series muy cortas → usar el span completo; para series largas es estable.

## Open Questions

- Valor de `MAX_GROSS_EXPOSURE` (¿4, 5?): default documentado, ajustable; no cambia el contrato.
- Valor por defecto del swap por instrumento: placeholder; se calibra con tasas reales del broker más adelante.
- Símbolo de energía denso para reemplazar BRENT: se evalúa al re-incluir energía (fuera de alcance).
