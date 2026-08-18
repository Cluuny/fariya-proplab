## 1. Estimación de vol segura ante huecos

- [x] 1.1 `engine.rolling_vol(prices, window)`: vol por instrumento sobre sus días propios (excluye ceros de ffill), anualizada por sus barras/año
- [x] 1.2 Test: la vol de un índice con huecos ≈ vol propia y NO la deflactada por ceros de relleno

## 2. Anclaje: nombrar lo verificado

- [x] 2.1 `SHARPE_REFERENCE.source`: externo = la serie ES el índice (endpoints); interno = 0.80 (geométrico) vs 0.82 (aritmético); NO es comparación contra un paper; pendientes anotados (endpoint final, tick independiente)

## 3. ffill en colas (limitación)

- [x] 3.1 (Sync en archivo) El spec `backtest-engine` anota que `ffill` extendería el último precio en una cola corta; limitación conocida para instrumentos de historia más corta

## 4. KPIs del reporte generados

- [x] 4.1 `scripts/report_kpis.py`: computa tests, PRs, instrumentos, specs, changes, holdout, Sharpe de referencia desde el repo
- [x] 4.2 Reporte HTML: tomar los KPIs de la salida del generador (corregir el desfase 69/9 → valores reales) y anotar que se derivan del repo

## 5. Cierre

- [x] 5.1 Toda la suite pasa (`uv run pytest`)
- [x] 5.2 Commit
