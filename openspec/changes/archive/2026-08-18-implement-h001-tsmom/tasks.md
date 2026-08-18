## 1. Señal TSMOM

- [x] 1.1 `tsmom(prices, *, lookback_months=12, vol_window=63, vol_target=0.08, max_gross, rebalance='BMS')` en `src/signals.py`: ret_12m gap-safe → signo → vol-inversa relativa → escalado ex-ante (un paso) → cap de bruto → rebalanceo mensual con holding
- [x] 1.2 Helper de escalado ex-ante (escalar rodante, shift(1), sin bucle de convergencia)
- [x] 1.3 Pureza: no muta `prices`, determinista, conforme al contrato (`validate_weights`)

## 2. Tests

- [x] 2.1 `tests/test_tsmom.py`: forma/pureza/determinismo; dirección (ret_12m>0 → long); rebalanceo mensual (pesos constantes entre BMS); invariante de exposición ≤ max_gross
- [x] 2.2 Test ex-ante: recomputar sobre la serie extendida con fechas futuras no cambia los pesos de las fechas originales
- [x] 2.3 Suite completa verde (`uv run pytest -q`)

## 3. Correr el veredicto

- [x] 3.1 `scripts/run_h001.py`: cargar los 9 parquet, construir Muestra A (FX+oro, eval ≥2004-01) y Muestra B (los 9, eval ≥2015-01)
- [x] 3.2 Especificación primaria (swap 0.3 bp) + sensibilidad (0.0, 1.0); Sharpe neto por (muestra × swap)
- [x] 3.3 Regla de zona marginal: si primaria ∈ [0.2,0.4] correr lookback 6m, intentos=4, deflated Sharpe, regla de decisión
- [x] 3.4 Emitir veredicto (por muestra, regla de dos muestras, contra la expectativa 0.40)

## 4. Registrar y cerrar

- [x] 4.1 Escribir el veredicto en `hypotheses/H001_tsmom.yaml` (`fecha_test`, `intentos_realizados`, `resultado`, `veredicto`, `estado`) — SIN tocar FALSADOR/metrica_exito/resultado_esperado
- [x] 4.2 Commit
