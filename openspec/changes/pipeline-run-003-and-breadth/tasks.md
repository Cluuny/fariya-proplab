# Tasks

## Bloque B — cribado de amplitud del terreno (primero, decisivo)
- [x] B.1 `scripts/terrain_breadth.py`: N_eff (Σλ)²/Σλ² por universo (CFD local, cripto fapi, ETF proxies Yahoo) + combinaciones
- [x] B.2 Medir cripto perps 30 (la medición clave, acceso ilimitado): N_eff 2.16
- [x] B.3 Techo de IR ≈ IC·√N_eff (IC 0.02/0.05) vs listones; nota de robustez a la frecuencia
- [x] B.4 `docs/terrain_breadth.md`: tabla + conclusión directa (NO para todos → cierre por amplitud)
- [x] B.5 `docs/program_verdict.md` §1.7: registrar el cierre por amplitud + reescribir el cierre

## Bloque A — run 003 (según la regla del bloque)
- [x] A.1 Run 003 NO se ejecuta (B cerró el programa; decirlo con el número es más informativo)
- [x] A.2 Regla `\b` en todos los gates de decisión (`estimate._NOT_STRATEGY` por `\b`)
- [x] A.3 Test genérico `tests/test_pipeline_word_boundary.py` (batería de palabras-trampa)
- [x] A.4 Nota de la regla en `docs/research_pipeline.md`

## Verificación
- [x] V.1 Suite verde; holdout intacto, sin pre-registro, sin API cableada
