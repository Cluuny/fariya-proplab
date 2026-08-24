# Pivote a cripto — Bloque 1: ingesta y persistencia

## Por qué

Se cierra el ciclo CFD/futuros como vehículo principal (`docs/program_verdict.md` sigue
vigente y no se revisa). Cripto se adopta porque el terreno es investigable a coste cero:
datos de libro gratuitos e ilimitados en `data.binance.vision`. **No se asume que hay
edge.** Este bloque es infraestructura: sin ingesta persistente y verificada no hay nada
que investigar, y ya se perdieron datos una vez.

## Qué cambia

- **Verificación de disponibilidad (1.1, bloqueante — PASA):** verificado por HTTP directo
  (2026-08-24) que el histórico de futuros USD-M tiene **bookTicker** (best bid/ask CON
  tamaños, ~199 MB/día BTCUSDT, IMPRESCINDIBLE para OFI), aggTrades (~22 MB) y bookDepth
  (~0.5 MB). El README de binance/binance-public-data NO lista bookTicker, pero existe.
- **Ingesta** (`src/crypto/ingest.py`): descarga de volcados diarios, verificación contra
  el SHA256 que publica Binance, lectura de bookTicker ORDENADA por (transaction_time,
  update_id) — los volcados vienen interleaved (issue #305) y sin ordenar el OFI sería
  basura.
- **Persistencia (1.4):** `data/raw_crypto/` inmutable (sólo lectura); `MANIFEST.sha256`
  versionado en git (los .zip no, son grandes y re-descargables); `verify_manifest` falla
  si un checksum no cuadra.
- **Reporte de calidad (1.5, mismo criterio que mató a BRENT)** (`quality.py`): huecos
  temporales, timestamps duplicados/desordenados, precios cero/negativos, tamaños
  negativos, libro cruzado, mantenimiento; **KILL si falta >25% de un período**.
- **Universo/ventana (1.2, 1.3):** sólo BTCUSDT perpetuo; empezar con 5 días midiendo
  GB/tiempo antes de escalar.
- CLI `scripts/crypto_ingest.py` (download/verify/quality), tests, `docs/crypto_pivot.md`.

## Impacto

- Nuevo paquete `src/crypto/` (ingest, quality), script, tests, doc de pivote, manifiesto
  versionado. Descargado y verificado 1 día real de BTCUSDT (bookTicker + aggTrades),
  reporte de calidad **OK**. Stdlib + pandas, sin nuevas deps. Sin delta de spec.
- Infraestructura/cribado: no consume intentos, no toca holdout, no pre-registra nada.
