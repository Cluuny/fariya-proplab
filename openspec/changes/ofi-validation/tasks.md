# Tareas

## 1. Fórmula OFI (exacta, §2.1)
- [x] 1.1 `compute_events`: e_n con desigualdades NO estrictas, literal del paper.
- [x] 1.2 `build_grid`: OFI_k por bin Δt, ΔP_k en ticks, profundidad media, opción
  exclude_price_changing.
- [x] 1.3 Exige input ordenado en el tiempo (ingest lo garantiza; issue #305).

## 2. Calibración
- [x] 2.1 `ols_white` (HC0) + regresiones por media hora, R² medio.
- [x] 2.2 `trade_imbalance` desde aggTrades (signo del agresor) + comparación.
- [x] 2.3 Relación β∝1/profundidad (log-log) y check excl. eventos que cambian precio.
- [x] 2.4 Criterio de aceptación comprometido: R²>0.40 Y OFI>trade imbalance.

## 3. Tests
- [x] 3.1 Fórmula e_n verificada A MANO (el test más importante).
- [x] 3.2 Caso sintético lineal ΔP=OFI/2D → R²≈1, β=1/2D; OLS/White; signo de TI.

## 4. Runner + validación sobre datos reales
- [x] 4.1 `scripts/ofi_calibrate.py`.
- [x] 4.2 Correr sobre BTCUSDT 2024-01-02: R² 0.638, OFI>TI (0.638>0.453), β∝1/depth
  (−1.171), excl-price 0.596 → PASA. `docs/ofi_validation.md`.
