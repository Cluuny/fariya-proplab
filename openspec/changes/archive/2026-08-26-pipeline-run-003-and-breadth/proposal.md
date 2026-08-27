# Run 003 + cribado de amplitud del terreno

## Why

Nueve familias murieron, muchas por AMPLITUD (H002 N_eff 3.41, H007 5.32, sectorial 1.29,
H008 2 instr). Antes de correr más pipeline, una pregunta aritmética sobre datos que YA existen
decide de raíz: **¿cuál es el N_eff MÁXIMO alcanzable con universos que podemos operar Y pagar
($125/mes), y su techo de IR supera algún listón?** Si NO para todos, es el cierre del programa
por amplitud — más informativo que cuatro corridas más. Por eso, y por la regla del bloque
(«B primero; si B cierra, la run 003 pierde sentido»), el orden es B → A.

## What Changes

**Bloque B — cribado de amplitud (DECISIVO):** `scripts/terrain_breadth.py` + `docs/terrain_breadth.md`.
N_eff = (Σλ)²/Σλ² de la correlación de retornos diarios, para cada universo accesible:
- Cripto perps 30 (Binance, GRATIS, acceso ilimitado): **N_eff 2.16 MEDIDO** (corr mediana 0.68;
  todo co-mueve con BTC). La medición más importante — es el universo sin barrera de acceso.
- CFD 17: 5.02 medido. ETFs sector/país/factor: 3.31 medido (replica, no añade). Futuros CME ~26
  (proxy ETF, requiere $50/mo): 8.15 — el más ancho. Combinaciones: 4.36 / 5.83.
- Techo de IR ≈ IC·√N_eff (IC 0.02 y 0.05) vs listones (CFD 0.64, cripto 0.65, duty-31% 0.96).
- **VEREDICTO: NO para todos.** Máximo alcanzable ~0.14 (futuros IC.05); robusto a frecuencia
  (mensual IC.05 → 0.49 < 0.64; superar 0.64 exigiría N_eff ≥ 14, inalcanzable). **Cierre del
  programa por amplitud** (más fundamental que el suelo de costes). Registrado en
  `docs/program_verdict.md` §1.7.

**Bloque A — run 003: NO SE EJECUTA.** Siguiendo la regla del propio bloque, como B cerró el
programa la run 003 pierde sentido y no se corre (decirlo con el número es más informativo). SÍ se
implementa la regla de higiene que el bloque pedía como spec: **todo gate de DECISIÓN por palabra
clave usa límite de palabra (`\b`), sin excepción** (tercer bug del mismo tipo: ict⊂predict,
carry⊂carrying, long-the⊂along-the) — `estimate._NOT_STRATEGY` ruteado por `\b`, + test genérico
`tests/test_pipeline_word_boundary.py` con batería de palabras-trampa, + nota en la spec del pipeline.

## Impact

- NUEVO: `scripts/terrain_breadth.py`, `docs/terrain_breadth.md`, `tests/test_pipeline_word_boundary.py`.
- MOD: `docs/program_verdict.md` (§1.7 cierre por amplitud + cierre reescrito), `src/pipeline/estimate.py`
  (_NOT_STRATEGY por `\b`), `docs/research_pipeline.md` (regla `\b`).
- Sin pre-registro, sin backtest, holdout intacto, API no cableada. Run 003 deliberadamente no ejecutada.
