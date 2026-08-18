# Datos (`data/`)

`data/raw/` está **git-ignorado** pero es **inmutable** y **re-descargable** con la
receta de abajo. `data/clean/` (parquet) es derivado por `python -m src.loaders`.

## Universo

10 instrumentos decorrelacionados por clase y geografía (ver `src/config.py`):
FX majors (EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD), oro (XAUUSD), índices
(SPX500=`USA500IDXUSD`, GER40=`DEUIDXEUR`, JPN225=`JPNIDXJPY`) y energía
(BRENT=`BRENTCMDUSD`).

Cobertura real de Dukascopy (menor a la pedida en varios): FX/oro desde 2003,
SPX500/JPN225 desde 2011-09, GER40 desde 2013-09, Brent desde 2011-09.

## Cómo poblar `data/raw/`

### Opción A — dukascopy-node (usada para el histórico actual; requiere Node)

```bash
npx -y dukascopy-node -i eurusd       -from 2003-05-05 -to 2026-08-17 -t d1 -f csv -v -dir data/raw
npx -y dukascopy-node -i gbpusd       -from 2003-05-05 -to 2026-08-17 -t d1 -f csv -v -dir data/raw
npx -y dukascopy-node -i usdjpy       -from 2003-05-05 -to 2026-08-17 -t d1 -f csv -v -dir data/raw
npx -y dukascopy-node -i audusd       -from 2003-08-04 -to 2026-08-17 -t d1 -f csv -v -dir data/raw
npx -y dukascopy-node -i usdcad       -from 2003-08-04 -to 2026-08-17 -t d1 -f csv -v -dir data/raw
npx -y dukascopy-node -i xauusd       -from 2003-05-05 -to 2026-08-17 -t d1 -f csv -v -dir data/raw
npx -y dukascopy-node -i usa500idxusd -from 2005-01-01 -to 2026-08-17 -t d1 -f csv -v -dir data/raw
npx -y dukascopy-node -i deuidxeur    -from 2005-01-01 -to 2026-08-17 -t d1 -f csv -v -dir data/raw
npx -y dukascopy-node -i jpnidxjpy    -from 2005-01-01 -to 2026-08-17 -t d1 -f csv -v -dir data/raw
npx -y dukascopy-node -i brentcmdusd  -from 2011-09-20 -to 2026-08-17 -t d1 -f csv -v -dir data/raw
```

dukascopy-node exporta CSV con `timestamp` en epoch-ms y nombres
`<sym>-d1-bid-<desde>-<hasta>.csv`. Normalizar a `<INSTRUMENTO>.csv` (el mapeo
inverso de `config.DUKASCOPY_SYMBOLS`), p. ej. `usa500idxusd-…csv → SPX500.csv`.
`loaders` acepta el `timestamp` epoch-ms directamente.

### Opción B — módulo Python nativo (sin Node)

```bash
python -m src.dukascopy --from 2003-05-05
```

`src/dukascopy.py` baja las velas diarias `.bi5` del feed público, las decodifica
(formato verificado contra una muestra real de EURUSD) y escribe `data/raw/<INST>.csv`.

## Procesar

```bash
python -m src.loaders     # raw → data/clean/*.parquet + reporte de calidad
```
