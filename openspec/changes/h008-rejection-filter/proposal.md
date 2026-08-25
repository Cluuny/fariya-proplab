# H008 — duty real (filtro de rechazo) antes del Bloque 4

## Por qué

La ficha declaró duty 0.20 y sobre eso calculó el listón (Sharpe activo 1.14). La muestra real
dio 642 edge-touch / 547 días = duty 59% — pero ése es COTA SUPERIOR porque falta el filtro de
RECHAZO (mid re-entra al VA en ≤3 barras de 1 min). Con duty 59% el listón activo baja pero el
coste sube por rotación; no se sabe el neto sin el número real. Hay que medir una sola cosa.

## Qué cambia

- **Medición (sin backtest, sin nulo, sin Δ Sharpe):** klines 1m del in-sample (ligeros,
  ~63 MB, manifestados). `scripts/h008_rejection_filter.py`: de los edge-touch, cuántos
  sobreviven al filtro de rechazo de la ficha.
  - edge-touch 643 (duty 59%) → **rechazo confirmado 341 (duty 31%)**, supervivencia 53%.
- **Listón recalculado sobre el duty REAL (0.31):**
  - Sharpe ACTIVO requerido 0.40/√0.31+0.245 = **0.961** (a priori 20% → 1.139).
  - round-trips/día 0.31; requerido bruto cripto (maker, funding evitado) **0.476**.
  - Binding: el activo ~0.96 (> suelo de coste 0.48). Más bajo que el 1.14 a priori, pero alto.
- **T efectiva final: ~189-341 (descuento ρ0.8) ≥ 150** → poder suficiente, NO underpowered.
- **(4) Desviación del pre-registro registrada** (sin tocar falsador/resultado_esperado): duty
  a priori 0.20 vs medido 0.31, con el listón recalculado. Visible en la ficha.
- **(5) Expectativa REFUTADA registrada:** resultado_esperado decía coincidencia >60-80% /
  redundancia; medido 26% [23,28], POC vs VWAP mediana 32 bps → los niveles de perfil NO son
  redundantes con niveles simples. Resultado limpio. MATIZ: distintos ≠ mejores; el Δ Sharpe del
  Bloque 4 decide.

## Impacto

- `scripts/h008_rejection_filter.py`, klines 1m manifestados, ficha (`resultado`), reporte.
  Raw discardable no aplica (1m klines caben). Suite 197 verde. **NO se corre el Bloque 4**; el
  listón está recalculado sobre el duty real y T ≥ 150. Holdout intacto. Sin delta de spec.
