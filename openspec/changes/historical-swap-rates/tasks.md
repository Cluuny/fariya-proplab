## 1. Carry histórico (A)

- [x] 1.1 Descargar series mensuales de tasas de política de BIS (WS_CBPOL, 8 divisas, 2003-2026) → `data/rates/policy_rates.csv`
- [x] 1.2 `src/rates.py`: cargar, reindexar a diario (ffill), `carry_matrix(index, instrumentos)` (fecha×instrumento); cruces aditivos; índices/metales
- [x] 1.3 `engine.backtest`: parámetro `carry_matrix` (si se pasa, carry variable en el tiempo; si no, escalar del CostModel)

## 2. Convención + calibración (B, C, D)

- [x] 2.1 Factor 365/261 en carry y margen (margen efectivo → 0.42 bp/d); documentado
- [x] 2.2 Validación cruzada broker vs tasas (dentro del 10%) escrita en el source
- [x] 2.3 `BROKER_MARGIN_MULT` con sensibilidad {1.0, 1.5}
- [x] 2.4 `data/README.md`: cómo regenerar `policy_rates.csv` desde BIS

## 3. Tests y cierre

- [x] 3.1 TEST OBLIGATORIO: EURUSD carry positivo en 2009-2015; + aditividad de cruces, variación temporal, factor
- [x] 3.2 Suite verde (90)
- [x] 3.3 Commit
