# Validación del OFI en cripto — Bloque 2 (PASA)

Implementación de la fórmula exacta de **Cont, Kukanov & Stoikov (2011, arXiv 1011.6402),
§2.1**, literal, con desigualdades NO estrictas:

    e_n = 1{P^B_n ≥ P^B_{n-1}}·q^B_n − 1{P^B_n ≤ P^B_{n-1}}·q^B_{n-1}
        − 1{P^A_n ≤ P^A_{n-1}}·q^A_n + 1{P^A_n ≥ P^A_{n-1}}·q^A_{n-1}
    OFI_k = Σ e_n sobre (t_{k-1}, t_k];   ΔP_k = (mid_k − mid_{k-1})/δ

La fórmula está verificada a mano en `tests/test_crypto_ofi.py` (e_n calculado a mano vs.
la implementación, más un caso sintético lineal ΔP = OFI/(2D) que recupera R²≈1 y β=1/2D).

## Test de calibración sobre datos REALES (BTCUSDT perp, 2024-01-02)

Regresión contemporánea `ΔP_k = α + β·OFI_k + ε` en submuestras de **media hora**,
**Δt = 10 s**, errores estándar de **White (HC0)**. 18.5M eventos → 48 submuestras.

| medida | cripto (medido) | paper (acciones) | ¿cumple? |
|---|---|---|---|
| **R² medio OFI** | **0.638** | ~0.65 | **SÍ** (umbral aceptación >0.40) |
| R² medio trade imbalance | 0.453 | ~0.32 | — |
| **(a) OFI mejor que trade imbalance** | 0.638 > 0.453 | 0.65 > 0.32 | **SÍ** (test MÁS discriminante) |
| **(b) β inversa a la profundidad** (pendiente log-log) | −1.171 | λ≈−1 | **SÍ** |
| **(c) excl. eventos que cambian precio** | 0.596 | 0.35-0.60 | **SÍ** (baja pero se mantiene) |
| β significativo (\|t_White\|>1.96) | 100% de las medias horas | ~100% | SÍ |

## Veredicto: el Bloque 2 PASA

El OFI reproduce en cripto la firma del paper: R² alto (~0.64), explica mejor que trade
imbalance, y β ∝ 1/profundidad con λ≈1. La implementación es **correcta** (los dos
diagnósticos estructurales —OFI>TI y la pendiente de profundidad ≈ −1— son justo los que
delatarían un bug, y ambos salen bien).

Notas honestas:
- El R² de **trade imbalance en cripto (0.453)** es más alto que en acciones (0.32): en
  cripto la información del flujo de trades explica más que en equities. Aun así, **OFI lo
  supera** → la condición (a) se cumple.
- El R² **excluyendo eventos que cambian precio (0.596)** queda en el borde superior del
  rango del paper: en cripto una fracción mayor del R² viene de eventos que NO mueven el
  mid (profundidad en el mejor nivel), consistente con un libro muy activo.

## Lo que este resultado NO dice

Esto valida que el **OFI es una variable bien medida y contemporáneamente informativa** del
cambio de precio — NADA sobre PREDICTIBILIDAD (el OFI y ΔP son del MISMO intervalo). La
curva de decaimiento predictivo (¿el OFI de ahora predice el ΔP futuro?) es el siguiente
change, y sólo se hace porque el Bloque 2 validó. No se ha establecido edge.

## Reproducir

```bash
python -m scripts.ofi_calibrate --symbol BTCUSDT --date 2024-01-02
```
