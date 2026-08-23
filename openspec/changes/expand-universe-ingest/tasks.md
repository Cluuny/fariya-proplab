## 1. Ingesta

- [x] 1.1 Descargar d1 de los 9 nuevos a `data/raw/<INSTRUMENTO>.csv` (reusando los CSVs de la auditoría)
- [x] 1.2 `config.INSTRUMENTS` 9 → 18 + `DUKASCOPY_SYMBOLS`/`DUKASCOPY_POINT`
- [x] 1.3 `python -m src.loaders` → 18 parquet + quality report; coberturas coinciden con la auditoría

## 2. Amplitud efectiva

- [x] 2.1 `scripts/effective_breadth.py`: N_eff (participation ratio) antes/después + aporte marginal
- [x] 2.2 `data/universe_expansion.md`: resultado (3.73 → 5.20) + recomendación (quitar US30, aporte −0.13)

## 3. Cierre

- [x] 3.1 Actualizar test de universo (18) y `data/README.md`
- [x] 3.2 Suite verde
- [x] 3.3 Commit
