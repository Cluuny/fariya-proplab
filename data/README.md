# Datos (`data/`)

`data/raw/` está **git-ignorado** pero es **inmutable** y **re-descargable** con la
receta de abajo. `data/clean/` (parquet) es derivado por `python -m src.loaders`.

## Universo

**18 instrumentos** operables limpios+live (ver `src/config.py` y la auditoría en
`data/universe_audit.md`):
- FX majors: EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD
- FX crosses (decorrelan del factor USD): EURJPY, GBPJPY, AUDJPY, EURAUD, GBPAUD, EURCHF
- Metales: XAUUSD (oro), XAGUSD (plata)
- Índices: SPX500=`USA500IDXUSD`, US30=`USA30IDXUSD`, GER40=`DEUIDXEUR`,
  JPN225=`JPNIDXJPY`, HK50=`HKGIDXHKD`

BRENT y el resto de energía/rates quedaron **fuera** por cobertura sparse
(auditoría Bloque 1). Cobertura real de Dukascopy: FX/oro/plata y cruces desde
2003-2005, SPX500/JPN225 desde 2011-09, GER40/US30/HK50 desde 2013.

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
# --- Bloque 2 (universo ampliado) — renombrar <sym>-d1-...csv a <INSTRUMENTO>.csv ---
npx -y dukascopy-node -i eurjpy      -from 2003-01-01 -to 2026-08-17 -t d1 -f csv -v -dir data/raw  # -> EURJPY.csv
npx -y dukascopy-node -i gbpjpy      -from 2003-01-01 -to 2026-08-17 -t d1 -f csv -v -dir data/raw  # -> GBPJPY.csv
npx -y dukascopy-node -i audjpy      -from 2003-01-01 -to 2026-08-17 -t d1 -f csv -v -dir data/raw  # -> AUDJPY.csv
npx -y dukascopy-node -i euraud      -from 2003-01-01 -to 2026-08-17 -t d1 -f csv -v -dir data/raw  # -> EURAUD.csv
npx -y dukascopy-node -i gbpaud      -from 2004-01-01 -to 2026-08-17 -t d1 -f csv -v -dir data/raw  # -> GBPAUD.csv
npx -y dukascopy-node -i eurchf      -from 2003-01-01 -to 2026-08-17 -t d1 -f csv -v -dir data/raw  # -> EURCHF.csv
npx -y dukascopy-node -i xagusd      -from 2003-01-01 -to 2026-08-17 -t d1 -f csv -v -dir data/raw  # -> XAGUSD.csv
npx -y dukascopy-node -i usa30idxusd -from 2013-09-30 -to 2026-08-17 -t d1 -f csv -v -dir data/raw  # -> US30.csv
npx -y dukascopy-node -i hkgidxhkd   -from 2013-06-03 -to 2026-08-17 -t d1 -f csv -v -dir data/raw  # -> HK50.csv
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

## Tasas de política históricas (para el carry del swap)

`data/rates/policy_rates.csv` (BIS WS_CBPOL, mensual, 8 divisas, 2003-2026). Se
usa para el `carry` direccional histórico del swap (`src/rates.py`). Regenerar:

```bash
# por cada divisa (US, XM=euro, JP, GB, AU, CA, CH, HK) desde la API v1 de BIS:
curl -s "https://stats.bis.org/api/v1/data/WS_CBPOL/M.US?startPeriod=2003-01"
# parsear los pares TIME_PERIOD/OBS_VALUE del SDMX-XML y volcar a policy_rates.csv
# (ver el script del change historical-swap-rates). Consultado 2026-08-22.
```

## COT — posicionamiento (CFTC Commitments of Traders)

`data/cot/<INSTRUMENTO>.csv` (8 con futuro US). Fuente: API pública CFTC Legacy
Futures-Only (dataset `6dca-aqww`), consultado 2026-08-23. Se filtra por
`cftc_contract_market_code` (estable) o `market_and_exchange_names`. Índice por fecha
de datos (martes); la publicación es +3 días (viernes) — ver `src/cot.py`. Cobertura y
duty cycle en `data/cot_coverage.md` (`scripts/cot_diagnostic.py`).
