## 1. Calendario: dropear barras de fin de semana

- [x] 1.1 En `loaders.clean`, descartar barras con `dayofweek >= 5` (Sáb/Dom); conservar orden y dedup
- [x] 1.2 Test: la serie limpia no contiene sábados ni domingos; el conteo de barras/año de FX cae de ~313 a ~260

## 2. Anualización por serie

- [x] 2.1 `engine.sharpe(returns, periods_per_year=None)`: si `None` y el índice es datetime, inferir `len / años_span`; si no, 252
- [x] 2.2 Test: dos series con distinto calendario se anualizan cada una con su conteo; el Sharpe de FX sube ~11% respecto al 252 fijo

## 3. Swap en costos

- [x] 3.1 `CostModel.swap` (cargo diario por |peso|), default placeholder documentado
- [x] 3.2 `engine.backtest`: aplicar `swap_cost_t = sum_i |w_{i,t-1}| · swap_i` cada día (peso mantenido, no turnover)
- [x] 3.3 Test: swap total escala con días mantenidos; buy&hold ahora incurre swap diario (turnover sigue 0 tras la entrada)

## 4. Relajar invariante de exposición

- [x] 4.1 `config.MAX_GROSS_EXPOSURE` (default 4); `signals.check_exposure`/`validate_weights` usan `max_gross`
- [x] 4.2 Test: exposición bruta 2-4× (vol-inversa típica) pasa; > `max_gross` falla; ajustar los tests existentes que asumían tope 1

## 5. Rename session_gap

- [x] 5.1 Renombrar `_detect_contract_jumps` → `_detect_session_gaps` y el tipo de anomalía `contract_jump` → `session_gap`
- [x] 5.2 Actualizar `report` y los tests que referencian `contract_jump`

## 6. Universo: BRENT fuera

- [x] 6.1 Quitar `BRENT` de `config.INSTRUMENTS`; conservar su mapeo/point con comentario (sparse; evaluar WTI)
- [x] 6.2 Ajustar `test_real_data.py` al universo sin BRENT

## 7. Referencia de Sharpe + hito 2 ámbar

- [x] 7.1 Re-generar `data/clean/` (parquets sin fin de semana) y recomputar el Sharpe de SPX500 buy&hold
- [x] 7.2 Fijar `SHARPE_REFERENCE.value` al nuevo número; `source` cita una estimación externa **price-return** del S&P 2011-2026 (no total-return)
- [x] 7.3 `test_real_data.py`: el motor reproduce el `SHARPE_REFERENCE` recomputado sobre datos reales

## 8. Reporte honesto

- [x] 8.1 Reporte HTML: hito 2 → ámbar; tabla con los 10 instrumentos + columna de días faltantes; caveat de dividendos (CFD price-return)
- [x] 8.2 Confirmar que `render_report` muestra `missing_days` de forma visible

## 9. Cierre

- [x] 9.1 Toda la suite pasa (`uv run pytest`); re-correr `python -m src.loaders` y confirmar el nuevo calendario y conteos
- [x] 9.2 Commit
