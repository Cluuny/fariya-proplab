## Context

Ver `proposal.md` — Why. El PDF no especifica método de descarga. Investigación del feed y las herramientas (agosto 2026):

- **Feed público de Dukascopy**: sirve archivos `.bi5` (LZMA-comprimidos, registros binarios de tamaño fijo) por instrumento. Además de ticks, expone **velas diarias** directamente con el patrón `{instrumento}/{año}/{tipo}_candles_day_1.bi5` — es decir, no hace falta bajar ticks y agregarlos a diario para EOD.
- **`dukascopy-node`** (JS, Leo4815162342): la herramienta más mantenida y de-facto estándar. CLI `npx dukascopy-node -i <inst> -from <d> -to <d> -t d1 -f csv`, 800+ instrumentos (incluye índices y commodities), salida CSV. Requiere Node.
- **`duka`** (Python, giuse88) y "Dukascopy Downloader" (Python): soportan timeframe D1; menos mantenidos que `dukascopy-node`.

## Goals / Non-Goals

**Goals:** descargar EOD diario para el universo → `data/raw/`, con mapeo de símbolos, determinista/idempotente, un runtime, robusto a fallos de red. Universo decorrelacionado (Nikkei/Brent).

**Non-Goals:** ticks/intradía (el sistema es EOD, §2.4 del documento); swap y `sum(|w|)` (`universe-and-costs`); cambiar `loaders` (sigue consumiendo `data/raw/` igual).

## Decisions

### D1 — Ruta recomendada: Python puro sobre velas diarias `.bi5` (un solo runtime)
Como Dukascopy expone **velas diarias directamente** (`*_candles_day_1.bi5`), la ruta Python pura es más simple de lo temido: descargar el/los archivo(s) diario(s) por instrumento, descomprimir LZMA, parsear el registro binario de tamaño fijo (timestamp + OHLC + volumen) y escribir CSV en `data/raw/`. Ventajas: un solo runtime (Python/uv, coherente con el resto), determinista, sin dependencia de Node ni de una CLI externa cuyo formato pueda cambiar. Dependencia añadida mínima (cliente HTTP; LZMA está en la stdlib de Python). **Alternativa (fallback):** envolver `dukascopy-node` vía subprocess — más robusto ante quirks del feed y con más cobertura de instrumentos, pero añade Node como dependencia del entorno. Se documenta como fallback si el endpoint de velas diarias resulta poco fiable para algún instrumento.

### D2 — Verificación del endpoint antes de fijar el parser
El formato exacto del registro `.bi5` de velas diarias y la ruta precisa (indexado de mes 0-based, tipo BID/ASK, endianness) se confirman contra un instrumento conocido (p. ej. EURUSD) comparando contra una fuente independiente antes de fijar el parser. Esto es parte de la implementación, no un supuesto.

### D3 — Mapeo de símbolos explícito y versionado
Tabla en `config` (p. ej. `DUKASCOPY_SYMBOLS: dict[str,str]`): `SPX500→USA500IDXUSD`, `GER40→DEUIDXEUR`, `UK100(retirado)`, `JPN225→JPNIDXJPY`, `BRENT→BRENTCMDUSD`, FX majors directos (`EURUSD→EURUSD`), `XAUUSD→XAUUSD`. Los símbolos exactos de Dukascopy se verifican contra su lista de instrumentos al implementar. Un instrumento del universo sin entrada = error visible (no archivo vacío).

### D4 — Universo corregido
Sustituir `NAS100` y `UK100` (redundantes con `SPX500`/`GER40`) por `JPN225` (Nikkei, Asia) y `BRENT` (energía). Universo resultante: 5 FX majors + XAUUSD (oro) + SPX500 + GER40 + JPN225 + BRENT — diversificado por clase y geografía. Se documenta el cambio y su razón (decorrelación para bajar volatilidad de portafolio).

### D5 — Escritura atómica e idempotente
Descargar a un archivo temporal y renombrar sobre el destino sólo al completar (escritura atómica) → un fallo no deja crudos parciales. Idempotencia: misma entrada → mismo archivo. Reintentos acotados con backoff y rate-limiting cortés hacia el feed.

## Risks / Trade-offs

- **El formato/endpoint de Dukascopy puede cambiar o no documentarse oficialmente** → Mitigación: verificación D2 contra un instrumento conocido; fallback a `dukascopy-node`; fallback manual (export web) documentado.
- **Calidad real de los datos** (feriados en 3 continentes, huecos del Nikkei en Golden Week, rollover del Brent) → no es riesgo de la ingesta sino su propósito: `loaders` los marca. La ingesta sólo debe entregar los crudos fielmente.
- **Cobertura de instrumentos en la ruta bi5 diaria** (¿todos los índices/commodities tienen velas diarias?) → verificar por instrumento en D2; los que fallen caen al fallback.
- **Dependencia de red en el flujo** → aislada al paso de ingesta; el pipeline de análisis sigue offline sobre `data/raw/`.

## Open Questions

- Símbolos exactos de Dukascopy para los índices/commodities (`JPNIDXJPY` vs `JPN225`, etc.): se fijan al verificar contra su lista de instrumentos en implementación; no cambian el contrato de la capability.
- ¿Un `.bi5` diario por año o uno por instrumento para todo el histórico? Se determina en D2; afecta el bucle de descarga, no el contrato.
