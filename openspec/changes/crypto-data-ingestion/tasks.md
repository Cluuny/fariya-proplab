# Tareas

## 1.1 Verificación de disponibilidad (bloqueante)
- [x] 1.1 Verificar por HTTP que bookTicker (best bid/ask con tamaños), aggTrades y
  bookDepth existen en futures/um/daily. bookTicker PRESENTE (~199 MB/día) → OFI posible.

## 1.2/1.3 Universo y ventana
- [x] 1.2 Universo inicial: sólo BTCUSDT perpetuo (USD-M).
- [x] 1.3 Ventana inicial 5 días; medir GB/tiempo antes de escalar (1 día ≈ 199 MB / 18.5M filas).

## 1.4 Persistencia
- [x] 1.4a `data/raw_crypto/` inmutable (el pipeline sólo lee); zips gitignored.
- [x] 1.4b `MANIFEST.sha256` versionado en git, checksum por archivo.
- [x] 1.4c Verificación contra el `.CHECKSUM` de Binance en la descarga.
- [x] 1.4d `verify_manifest` falla si un checksum no cuadra (o falta un archivo).

## 1.5 Reporte de calidad
- [x] 1.5 Huecos, timestamps duplicados/desordenados, precios cero, tamaños negativos,
  libro cruzado, mantenimiento; KILL si falta >25% de un período. Ordena al leer (issue #305).

## Verificación end-to-end + entregables
- [x] E1 Descargado y verificado 1 día real (BTCUSDT bookTicker + aggTrades); SHA256 cuadra.
- [x] E2 Reporte de calidad sobre el día real: OK (0 precios cero, 0 cruzado, hueco máx 2.3s).
- [x] E3 `docs/crypto_pivot.md`; CLI `scripts/crypto_ingest.py`; tests verdes.
