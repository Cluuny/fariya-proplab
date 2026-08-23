## 1. Modelo direccional

- [x] 1.1 `CostModel`: separar `carry` (signed) y `swap_margin` (unidireccional); renombrar el viejo `swap`
- [x] 1.2 `engine.backtest`: `swap_cost = swap_margin·|w_prev| − carry·w_prev`
- [x] 1.3 Actualizar runners de hipótesis muertas (`swap=` → `swap_margin=`, carry=0 → reproducen veredictos)

## 2. Calibración con datos reales (documentada, no inventada)

- [x] 2.1 `carry` desde tasas de política publicadas (UniRateAPI, 2026-08-22); cruces aditivos; índices/metales por financing±yield
- [x] 2.2 `swap_margin` desde tabla long/short de broker (afterprime, 2026-08-23; validado vs FTMO); `BROKER_MARGIN_MULT`
- [x] 2.3 Bloque SWAP_CALIBRATION en `config` con fuentes, fechas, método y limitación (snapshot dinámico)

## 3. Tests y validación

- [x] 3.1 Tests: larga en carry positivo RECIBE swap; margen siempre resta; cartera que cosecha carry < unsigned
- [x] 3.2 Suite verde (86)
- [x] 3.3 Validar impacto real: H007-A 0.184→0.182 (el modelo no rescata trend; el drag era real; desbloquea H002)

## 4. Cierre

- [x] 4.1 Commit
