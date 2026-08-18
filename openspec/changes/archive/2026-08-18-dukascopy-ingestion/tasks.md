## 1. Universo y mapeo de símbolos

- [x] 1.1 Corregir el universo en `src/config.py`: sustituir `NAS100` y `UK100` por `JPN225` (Nikkei) y `BRENT`; documentar la razón (decorrelación)
- [x] 1.2 Añadir tabla de mapeo `DUKASCOPY_SYMBOLS` (interno → símbolo Dukascopy), versionada; validación de que todo instrumento del universo tiene mapeo
- [x] 1.3 Test: cada instrumento del universo tiene mapeo; un instrumento sin mapeo produce un error explícito

## 2. Verificación del endpoint (D2 — antes de fijar el parser)

- [x] 2.1 Confirmar contra EURUSD la ruta y el formato del `.bi5` de velas diarias (indexado de mes, tipo BID/ASK, endianness, layout del registro), comparando contra una fuente independiente
- [x] 2.2 Confirmar disponibilidad de velas diarias para los índices/commodities del universo (JPN225, BRENT, SPX500, GER40); marcar los que caigan al fallback

## 3. Downloader (Python puro — ruta recomendada)

- [x] 3.1 Implementar `src/dukascopy.py`: por instrumento y rango, descargar el/los `.bi5` diario(s), descomprimir LZMA (stdlib), parsear a (fecha, OHLC)
- [x] 3.2 Escritura atómica (temporal → rename) e idempotente hacia `data/raw/` en el formato que `loaders` acepta
- [x] 3.3 Reintentos acotados con backoff y rate-limiting; un fallo tras reintentos no deja crudo parcial y se reporta
- [x] 3.4 Punto de entrada CLI `python -m src.dukascopy` (universo + rango de fechas configurables)
- [x] 3.5 Documentar el fallback `dukascopy-node` (subprocess) y el fallback manual (export web) para instrumentos problemáticos

## 4. Integración con la capa de datos

- [x] 4.1 Verificar E2E: `python -m src.dukascopy` → `data/raw/` → `python -m src.loaders` corre y produce el reporte de calidad marcando anomalías reales
- [x] 4.2 Fijar `SHARPE_REFERENCE` real en `config.py` con el Sharpe histórico de un índice sobre los datos reales (desbloquea el hito 2 en verde)

## 5. Tests

- [x] 5.1 Test de idempotencia y escritura atómica (con un `.bi5` de muestra/fixture, sin red)
- [x] 5.2 Test del parser `.bi5` diario contra un registro conocido
- [x] 5.3 Test: fallo de red simulado no deja archivo parcial
- [x] 5.4 Toda la suite pasa (`uv run pytest`)

## 6. Cierre

- [x] 6.1 Descargar el universo real 2005→hoy y graficar las 10 curvas para revisión humana ("mirarlas con los ojos", §8.2)
- [x] 6.2 Commit
