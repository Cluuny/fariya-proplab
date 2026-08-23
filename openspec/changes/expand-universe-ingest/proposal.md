## Why

Bloque 2 del plan: con la auditoría del Bloque 1 (`data/universe_audit.md`) decidida (opción a: limpio + live), ingerir el universo ampliado y medir la **amplitud efectiva** (autovalores de la matriz de correlación) antes/después — la métrica de progreso real, no el conteo de instrumentos.

## What Changes

- **`config.INSTRUMENTS` 9 → 18**: añade 6 cruces FX (EURJPY, GBPJPY, AUDJPY, EURAUD, GBPAUD, EURCHF), plata (XAGUSD), Dow (US30) y Hang Seng (HK50). Mapeos en `DUKASCOPY_SYMBOLS`/`DUKASCOPY_POINT`; `COSTS` los cubre automáticamente (comprehension).
- **Ingesta**: 9 CSVs d1 nuevos en `data/raw/` → `loaders` regenera `data/clean/*.parquet` (18) + `data/quality_report.md`. Coberturas coinciden con la auditoría.
- **`scripts/effective_breadth.py`** (nuevo): N_eff = participation ratio de los autovalores de la correlación, antes/después, con aporte marginal por instrumento.
- **`data/universe_expansion.md`** (entregable): resultado de amplitud efectiva + recomendación.
- Test de universo actualizado (9 → 18, cada símbolo mapeado).

Resultado (verificado): **N_eff 3.73 → 5.20** (+1.47, ×1.39; techo de Sharpe ×1.18). Los cruces FX aportan menos de 1 cada uno (son combinaciones de majors); **US30 aporta −0.13** (redundante con SPX500); los diversificadores reales son EURCHF (+0.51), GBPAUD (+0.41), HK50 (+0.39).

Fuera de alcance: pre-registrar H005/H007 (siguiente paso); quitar US30 (recomendado, decisión del usuario).

## Capabilities

### New/Modified Capabilities
<!-- Ninguna: cambio de universo (config) + ingesta + tooling. skip_specs=true. -->

## Impact

- **Código**: `src/config.py` (universo), `scripts/effective_breadth.py` (nuevo), `tests/test_scaffolding.py` (conteo). `data/README.md` actualizado.
- **Artefactos**: `data/clean/*.parquet` (18, gitignored), `data/quality_report.md`, `data/universe_expansion.md` (entregable).
- Universo operable duplicado; amplitud efectiva +1.5. Habilita las hipótesis sobre el universo ampliado.
