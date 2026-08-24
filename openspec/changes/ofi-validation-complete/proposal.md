# Cerrar la validación del OFI (Bloque A) y el cribado de decaimiento (Bloque B)

## Por qué

El OFI está validado contemporáneamente (R²~0.64) pero faltaba (A) cerrar la validación —
regresión conjunta OFI+TI, más días/regímenes, y verificar unidades— y (B) el cribado que
DECIDE: ¿el OFI predice el precio o sólo lo describe? Un R² contemporáneo alto es compatible
con cero predictibilidad (el error de H003). Sin el decaimiento predictivo cruzado con el
suelo de costes, no hay decisión sobre order flow.

## Qué cambia

**Bloque A — cerrar la validación (`calibrate.py`, `scripts/ofi_validate_full.py`):**
- Regresión CONJUNTA `ΔP = α + θ_O·OFI + θ_T·TI` por media hora con SE de White
  (`ols_white_multi`, `joint_regressions`).
- 4 días de regímenes distintos elegidos por vol realizada ANTES de correr el OFI
  (klines 1m). Las 4 verificaciones se sostienen en los 4.
- ĉ y verificación de unidades (`estimate_c_and_units`).
- **Hallazgo (A.1):** el trade imbalance NO queda subsumido en cripto (t 6-9, sig 96-100%,
  al revés que el paper) → mucha señal está en aggTrades (archivos ~10× menores). El OFI aún
  aporta incremental (R²_conj 0.74-0.85 ≫ R²_TI 0.40-0.51).
- **Hallazgo (A.3):** ĉ≈2.5-3.0 (≈5-6× el 0.45 del paper), ESTABLE a través de escalas →
  no es bug de unidades ni artefacto de agregación; el book display sobreestima la profundidad
  efectiva ~5× (liquidez fugaz). No afecta al OFI como predictor ni al Bloque B.

**Bloque B — el cribado que decide (`decay.py`, `scripts/ofi_decay.py`):**
- Curva de decaimiento: return futuro ~ OFI a 1s…60min; contemporáneo vs predictivo lado a
  lado; IC por block bootstrap; n independientes.
- Cruce con el suelo de costes (Bloque 3): Sharpe implícito vs listón a la frecuencia que
  impone cada horizonte (maker/taker), y la BRECHA.
- Criterio y expectativa comprometidos ANTES de correr.

## Resultado

**VEREDICTO: ORDER_FLOW_CERRADO.** R² predictivo ~0 en todos los horizontes (dos órdenes de
magnitud bajo el contemporáneo); la brecha con el suelo es negativa en todos (mejor: 30 min,
−0.77 maker). Order flow se cierra como familia (como H005/H006/COT). Expectativa (B.5)
CONFIRMADA. Cero pesos gastados; no se procede a modelo de fills ni pre-registro.

## Impacto

- `src/crypto/calibrate.py` (+joint/ĉ), `src/crypto/decay.py` (nuevo), scripts, tests
  (`test_crypto_decay.py`), `docs/ofi_validation_complete.md`, artifact HTML. 4 días reales
  descargados/verificados/manifestados. Suite 164 verde. Sin nuevas deps. Sin delta de spec.
