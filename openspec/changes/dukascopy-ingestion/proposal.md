## Why

El PDF (§6.3, §8.2) sólo dice "usar Dukascopy" y "descargar diarios 2005→hoy" — no da método ni herramienta, así que hoy los datos son manuales. Es el cuello de botella real: el hito 2 no se pone en verde de verdad hasta correr sobre datos reales, y el bug del precio-cero que encontramos sintéticamente es un anticipo de la basura que traerá el feed real. Automatizar la descarga con una capa de mapeo de símbolos desbloquea todo el Bloque C.

## What Changes

- **Nueva capa de ingesta**: un downloader que baja barras diarias EOD de Dukascopy para el universo configurado y las escribe en `data/raw/` en el formato que `loaders` ya valida. Determinista e idempotente.
- **Mapeo de símbolos**: los símbolos internos (`SPX500`, `GER40`, …) NO existen en Dukascopy; hay que mapearlos a los suyos (`USA500IDXUSD`, `DEUIDXEUR`, `BRENTCMDUSD`, …). Capa de mapeo explícita y versionada.
- **Corrección del universo** (hallazgo del reviewer): el universo actual son 4 índices de renta variable (`SPX500`, `NAS100`, `GER40`, `UK100`), 3 correlacionados, sin energía ni Asia — la peor composición para un portafolio cuyo fin es bajar volatilidad por decorrelación. Se sustituyen **NAS100 y UK100 por Nikkei (JPN225) y Brent (BRENT)**.
- **Fallback manual documentado**: si el feed falla o falta un instrumento, el procedimiento manual (export histórico web de Dukascopy) queda documentado.

Los datos bajados pasan por la validación de calidad de `loaders` (gaps, ceros, retornos >5σ, saltos de contrato), que atrapará los feriados desalineados, huecos del Nikkei y rollover del Brent.

## Capabilities

### New Capabilities
- `data-ingestion`: Descarga automática, determinista e idempotente de barras diarias EOD desde el feed público de Dukascopy hacia `data/raw/`, con mapeo explícito de símbolos internos→Dukascopy y un universo decorrelacionado.

### Modified Capabilities
<!-- data-pipeline no cambia de comportamiento: sigue consumiendo data/raw/ igual. -->

## Impact

- **Código**: nuevo módulo de descarga (p. ej. `src/dukascopy.py`), tabla de mapeo de símbolos y universo corregido en `src/config.py`, punto de entrada CLI (`python -m src.dukascopy`).
- **Dependencias**: según la ruta elegida (ver `design.md` — recomendación: Python puro sobre las barras diarias `.bi5`, sin Node); posible dep. ligera de HTTP.
- **Datos**: `data/raw/` deja de ser manual; se llena con un comando. `data/raw/` sigue siendo inmutable para `loaders`.
- **Red**: introduce una dependencia de red en el paso de ingesta (no en el pipeline de análisis, que sigue operando sobre archivos locales). Rate-limiting y reintentos necesarios.
- **Fuera de alcance**: término de swap en `CostModel`/`engine` y la decisión `sum(|w|)≤1` (van en `universe-and-costs`); el objetivo umbral del simulador (sem 9-10).
