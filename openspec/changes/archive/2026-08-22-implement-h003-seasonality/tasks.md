## 1. Señal TOM

- [x] 1.1 `_tom_mask(index, first_n=3, last_n=1)` en `src/signals.py`: True en días TOM (~19%)
- [x] 1.2 `_long_inverse_vol(prices, active_mask, *, vol_window, vol_target, max_gross)`: long-only vol-inversa ex-ante, activo sólo en la máscara; compartido con el nulo
- [x] 1.3 `tom_seasonal(prices, *, window=(-1,3), ...)` = `_long_inverse_vol` con la máscara TOM; pura, determinista, long-only, conforme al contrato

## 2. Tests

- [x] 2.1 `tests/test_tom_seasonal.py`: forma/pureza/determinismo; long-only; activo sólo en ventana TOM (~19% de días); invariante de exposición
- [x] 2.2 Test ex-ante (extender con futuro no cambia pesos pasados)
- [x] 2.3 Suite completa verde

## 3. Correr el veredicto (in-sample, holdout intacto)

- [x] 3.1 `scripts/run_h003.py`: cargar 3 índices, cortar a in-sample (2011-09-19 → 2023-08-16), NUNCA tocar el holdout
- [x] 3.2 Existencia: contraste de medias TOM vs no-TOM (por instrumento + pooled), IC 95% block bootstrap
- [x] 3.3 Explotabilidad: Sharpe neto TOM (swap 0.3 + sensibilidad) vs benchmark nulo (1000 máscaras aleatorias, p95)
- [x] 3.4 Poder: IC 95% del Sharpe; estado `underpowered` si el IC cruza el p95 del nulo
- [x] 3.5 Diagnósticos: turnover_anual, sharpe_zero_cost, max DD/vol, tripwire max_gross
- [x] 3.6 Veredicto (viable_insample / muerta / underpowered) contra el falsador relativo

## 4. Registrar y cerrar

- [x] 4.1 Escribir veredicto en `hypotheses/H003_seasonality.yaml` (fecha_test, estado, resultado) SIN tocar FALSADOR/metrica_exito/resultado_esperado
- [x] 4.2 Generar `results/H003/report.md` (determinista)
- [x] 4.3 Actualizar `hypotheses/QUEUE.md` con el resultado; commit
