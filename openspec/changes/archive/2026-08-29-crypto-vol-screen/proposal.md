# Cribado de amplitud y prima de volatilidad en cripto (Deribit)

## Why

El terreno de cripto SPOT está cerrado (N_eff 2.16), pero la superficie de VOLATILIDAD IMPLÍCITA
nunca se tocó: H004 seguía rechazada_por_datos cuando esa restricción CAMBIÓ — Deribit publica DVOL
y opciones BTC/ETH por API pública gratuita. La vol implícita NO es recombinación del precio (info
ortogonal, como EURCHF), así que podría aportar amplitud. Es un CRIBADO (no hipótesis): no consume
intentos, no toca holdout.

## What Changes

`scripts/crypto_vol_screen.py` + `docs/crypto_vol_screen.md` (datos REALES de Deribit + Binance):
- **D1 cobertura:** DVOL (IV ~30d ATM) BTC/ETH diario + perp OHLC → prima IV−RV construible; **la
  cadena histórica de opciones NO es reconstruible gratis** (skew/estructura temporal no medibles) →
  la amplitud medida es cota inferior. Honesto, verificado antes de construir.
- **D2 amplitud:** N_eff spot 2.16 · vol-solas 3.88 · combinado **3.08** (vol aporta +0.92, por
  DEBAJO de la expectativa 4-5).
- **D3 IC:** dos objetivos — carry (IV−RV_fwd, comparte IV_t → IC 0.14 MECÁNICO, IC95 cruza 0) vs
  timing (−ΔIV, limpio → IC 0.03). Cola IZQUIERDA (skew −0.6 a −0.9). 63 obs independientes.
- **D4 IR** = IC·√(12·3.08): 0.20 (timing) a 0.85 (carry), ambos **INDETERMINADO** (banda cruza 0.65).
- **D5 expectativa:** cumplida en lo central (indeterminado/marginal), refutada en amplitud (3.08<4-5).
- **Bloque 5:** el suelo de costes de OPCIONES (no modelado) probablemente cierra lo indeterminado.

**VEREDICTO: INDETERMINADO con sesgo a NO.** No se pre-registra, no se reabre H004 a hipótesis, no
cumple C2 (IC≥0.10 con CI que no cruza). La última clase de datos accesible queda medida.

## Impact

- NUEVO: `scripts/crypto_vol_screen.py`, `docs/crypto_vol_screen.md`, `tests/test_crypto_vol_screen.py`.
- Sin ficha, sin pre-registro, holdout intacto, sin consumir intentos.
