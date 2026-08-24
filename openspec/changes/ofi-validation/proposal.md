# Pivote a cripto — Bloque 2: validar el OFI

## Por qué

Antes de investigar cualquier hipótesis de order flow hay que probar que el OFI está
**bien implementado**. El paper de Cont, Kukanov & Stoikov (2011) da un criterio de
aceptación falsable (R² alto en regresión contemporánea, y OFI mejor que trade imbalance).
Si el OFI está mal, todo lo que venga después es basura — así que se valida primero, sobre
datos reales, con un criterio comprometido.

## Qué cambia

- **`src/crypto/ofi.py`**: fórmula exacta §2.1 (desigualdades NO estrictas), `compute_events`,
  `build_grid` (rejilla Δt, ΔP en ticks, profundidad media), `trade_imbalance` (signo del
  agresor desde aggTrades), y la opción `exclude_price_changing` para la verificación (c).
  Nota crítica: exige input ordenado en el tiempo (los volcados vienen interleaved).
- **`src/crypto/calibrate.py`**: OLS con SE de White (HC0), regresiones por media hora,
  R² medio, relación β∝1/profundidad (log-log), comparación con trade imbalance.
- **Criterio de aceptación comprometido**: R² medio > 0.40 **y** OFI mejor que trade
  imbalance (el test más discriminante). Verificaciones secundarias (b) y (c) del paper.
- **`tests/test_crypto_ofi.py`**: la fórmula e_n verificada A MANO (el test más importante)
  + caso sintético lineal + OLS/White + signo de trade imbalance.
- **`scripts/ofi_calibrate.py`** y **`docs/ofi_validation.md`** con el resultado real.

## Resultado (BTCUSDT perp, 2024-01-02, datos reales)

**PASA.** R² medio OFI **0.638** (paper ~0.65), OFI > trade imbalance (0.638 vs 0.453),
β∝1/profundidad con pendiente −1.171, R² excl. eventos que cambian precio 0.596. Reproduce
la firma del paper → implementación correcta.

## Impacto

- `src/crypto/ofi.py`, `calibrate.py`, script, tests, doc. Sin nuevas deps. Sin delta de
  spec. Infra/cribado: valida una MEDICIÓN, no predictibilidad; no establece edge.
- Explícito: la curva de decaimiento predictivo es el siguiente change y sólo procede
  porque este bloque validó.
