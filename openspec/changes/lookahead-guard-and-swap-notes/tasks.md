## 1. Test de look-ahead (prerrequisito)

- [x] 1.1 `tests/test_lookahead.py`: señal tramposa `sign(ret.shift(-1))` → `sharpe > 5`; honesta `sign(ret.shift(1))` → `sharpe < 2`, sobre precios sintéticos deterministas
- [x] 1.2 Confirmar que pasa con la convención actual del motor (`w.shift(1)·ret_t`)

## 2. Hito 2 verde — anclaje de ventana exacta

- [x] 2.1 Recomputar `SHARPE_REFERENCE`: `value ≈ 0.80`, `window` = "2011-09-19 → 2026-08-14", `tolerance` 0.10; `source` documenta que el nivel inicial 1204.1 = cierre público real del S&P 500 ese día (verificación externa)
- [x] 2.2 `test_real_data.py`: el motor reproduce el nuevo `SHARPE_REFERENCE` (gross buy&hold SPX500)

## 3. Comentario del swap

- [x] 3.1 `CostModel.swap`: corregir el comentario "~3bp/día" → "~0.3bp/día" (0.00003 = 0.3bp)

## 4. Swap sin dirección — bloqueante de H002 (spec)

- [x] 4.1 (Sync en archivo) El delta MODIFICA el requisito de costos de `backtest-engine` con la limitación conocida (swap unsigned; bloqueante de H002); verificar coherencia con el código

## 5. Reporte

- [x] 5.1 Reporte HTML: hito 2 → verde; nota del test de look-ahead como guard de la capa de señales; caveat del swap-sin-dirección para H002

## 6. Cierre

- [x] 6.1 Toda la suite pasa (`uv run pytest`)
- [x] 6.2 Commit
