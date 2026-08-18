## 1. Fix del doble conteo

- [x] 1.1 Reescribir `_detect_contract_jumps(df, sigma)` para z-scorear el gap de apertura `log(open_t / close_{t-1})` y marcar `|z|>sigma`; si no hay columna `open`, devolver vacío
- [x] 1.2 Actualizar la llamada en `validate` para pasar el DataFrame (no los retornos close-to-close)

## 2. Tests del fix

- [x] 2.1 Test: una serie con un gap de apertura grande pero sin retorno close-to-close anómalo marca `contract_jump` y NO `anomalous_return`
- [x] 2.2 Test: una serie con un outlier close-to-close SIN gap de apertura marca `anomalous_return` y NO `contract_jump` (dejan de coincidir)
- [x] 2.3 Ajustar el test existente que asumía el conteo duplicado, si aplica

## 3. Verificación en código de los datos reales

- [x] 3.1 `tests/test_real_data.py` (skip si `data/clean/` sin parquets): los 10 instrumentos del universo tienen parquet
- [x] 3.2 El buy&hold de `SHARPE_REFERENCE.instrument` reproduce `SHARPE_REFERENCE.value` ± `tolerance` sobre datos reales (verificación del motor = hito 2)
- [x] 3.3 `validate` marca al menos un `anomalous_return` en el histórico de una FX major (evento real)

## 4. Cierre

- [x] 4.1 Toda la suite pasa (`uv run pytest`); re-correr `python -m src.loaders` y confirmar que los conteos ya no coinciden
- [x] 4.2 Commit
