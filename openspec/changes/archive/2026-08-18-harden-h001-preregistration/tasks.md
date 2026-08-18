## 1. Corregir la ficha (hypotheses/H001_tsmom.yaml)

- [x] 1.1 `universo_test` → dos muestras separadas: A (FX+oro, 2004-2026, incluye 2008) y B (los 9, 2015-2026, lookback completo)
- [x] 1.2 `FALSADOR`: devolver la cláusula post-2010 como regla de dos muestras (si A≥0.4 y B<0.2 → el hallazgo es la degradación post-2010; falsador de nivel <0.2 se evalúa por muestra)
- [x] 1.3 `zona_marginal` [0.2, 0.4]: `un_chequeo_robustez` (una variante lookback 6m, contada como intento n=2, deflated Sharpe reportado, ninguna más)
- [x] 1.4 `resultado_esperado`: sharpe_central ~0.40, rango [0.25, 0.60], derivación Grinold-Kahn, y `desviaciones` con dirección esperada por cada adaptación
- [x] 1.5 `sensibilidad_costos`: swap_bp_dia [0.0, 0.3, 1.0], las tres reportadas; si cruza el falsador → veredicto sobre el placeholder
- [x] 1.6 `sizing`: precisar que el escalado a 8% es **ex-ante** (escalar rodante, sólo vol observada hasta cada fecha), no vol realizada de toda la serie
- [x] 1.7 `rebalanceo` + `alineacion`: día de decisión determinista (primer día hábil del mes) y política de alineación escrita (unión de fechas, ffill precio, retorno del cruce al día de reapertura)
- [x] 1.8 Nota explícita en la ficha: la enmienda es pre-ejecución (`intentos_realizados: 0`, `fecha_test: null`); el falsador se congela tras el primer test

## 2. Cierre

- [x] 2.1 Verificar que el YAML sigue siendo válido (parsea) y que sigue `estado: pre_registrado`, `intentos_realizados: 0`
- [x] 2.2 Commit ANTES de cualquier código de señal
