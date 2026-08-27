# Cribado aritmético del candidato + refinamiento del eje

## Why

La run 002 dejó dos cabos: (a) el primer candidato que superó E3 (Sectoral Intramonth
Momentum, 0.55 > 0.44) con bandera roja de sobreajuste, que hay que CRIBAR con aritmética
antes de considerar pre-registro (mismo patrón barato que A.4 de H002 y COT); y (b) el eje
`es_estrategia_operable` dejó pasar 4 no-estrategias que E4 atrapó — hay que refinarlo. Además
se documenta (sin decidir) el caso de suscribir Quantpedia Premium, apoyado por primera vez en
una densidad MEDIDA.

## What Changes

1. **Cribado aritmético del candidato** (`src/pipeline/candidate_screen.py` + `scripts/screen_sectoral.py`
   + `docs/candidate_sectoral_screen.md`), SIN backtest: (1.1) Deflated Sharpe (Bailey & López de
   Prado) contando el espacio de búsqueda de 3 patas calendáricas; (1.2) nulo de exposición
   compartida (el TOM ≈ beta de mercado, lección H003); (1.3) amplitud efectiva + IC del Sharpe;
   (1.4) operabilidad real. **VEREDICTO: cribado_muere** por aritmética (el IC [0.17,0.93] incluye
   el listón 0.44 → irresoluble; deflación a N≈50-100 alcanza el listón; nulo compartido ~0.52 se
   come el 0.55). (1.4) NO es el bloqueante (corrección honesta: universo ETF estable, datos
   baratos). NO se pre-registra, no consume intento, no requiere ficha.
2. **Refinar `es_estrategia_operable`** (`src/pipeline/estimate.py`): (a) exigir una POSICIÓN
   direccional con LÍMITE DE PALABRA — los falsos positivos «carry»⊂«carrying», «long the»⊂«along
   the» eran bugs de subcadena; (b) rechazo por HORIZONTE INOPERABLE (< 1 min, suelo de costes
   intradía); (c) +descalificadores meta/tooling. Regresión: los 4 falsos positivos de la run 002
   mueren en E2.5 y el candidato sectorial sobrevive hasta E3 (además del test de la run 001).
3. **Decisión de fuentes documentada, SIN ejecutar** (`docs/pipeline_source_decision.md`): el caso
   Quantpedia Premium con la densidad medida (Quantpedia 10% real vs arXiv 0%), a favor y en
   contra, «no decidir todavía, dejar reposar».

## Impact

- NUEVO: `src/pipeline/candidate_screen.py` (+tests), `scripts/screen_sectoral.py`,
  `docs/candidate_sectoral_screen.md`, `docs/pipeline_source_decision.md`.
- MOD: `src/pipeline/estimate.py` (eje refinado), `tests/test_pipeline_strategy_axis.py` (regresión run 002).
- Sin pre-registro, sin backtest, holdout intacto, API no cableada, sin cambio de veredicto de familias.
