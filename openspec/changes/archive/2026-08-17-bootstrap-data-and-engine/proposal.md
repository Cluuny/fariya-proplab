## Why

PropLab es una fábrica de veredictos: convierte una hipótesis de trading en un número medido (`P(pasar el challenge)`) de forma repetible. El documento maestro impone una regla de secuencia innegociable — "no se automatiza un proceso que nunca se ha hecho a mano" — por lo que el Flujo 1 (Técnico) se construye antes que cualquier estrategia o investigación. Este change entrega el **Bloque A del cronograma (semanas 1-3)**: la infraestructura mínima que permite cerrar un ciclo antes de escribir el núcleo del simulador. Sin datos limpios y un motor verificado, cualquier veredicto posterior es ruido.

## What Changes

- Se establece la estructura plana del repositorio (sección 3.3) **directamente en la raíz del proyecto** (este directorio ya es la raíz `prop-lab`; NO se crea subcarpeta `prop-lab/`).
- Se añade proyecto Python gestionado con `uv` (`pyproject.toml`), dependencias `pandas` y `numpy` (`polars` opcional).
- **Nueva capa de datos** (`src/loaders.py`): convierte dumps crudos de Dukascopy (`data/raw/`, inmutable) en parquet limpio (`data/clean/`, uno por instrumento) con validación de calidad (gaps, ceros, duplicados, retornos >5σ, feriados, saltos de contrato) y un reporte de calidad legible por instrumento.
- **Nuevo contrato de señal** (`src/signals.py`): protocolo de funciones puras `(prices, ...) -> pesos objetivo` (sin estado, sin I/O, `sum(|pesos|) <= 1`) más una señal trivial de ejemplo (buy & hold) para verificar el motor. Este contrato es la futura interfaz con el Flujo 2.
- **Nuevo motor de backtest** (`src/engine.py`): recibe un DataFrame de pesos objetivo y devuelve retornos netos aplicando comisión, spread, slippage e impacto. Único componente que toca costos.
- **Nueva capa de reporte** (`src/report.py`): un comando regenera todo (equity curve, Sharpe, max drawdown, distribución de retornos) con reproducibilidad total.
- Se crean como carpetas vacías/placeholder los directorios de fases posteriores: `hypotheses/`, `notebooks/`, `results/`, y un stub `src/challenge.py` (implementación fuera de alcance).

Fuera de alcance (changes posteriores): implementación de `challenge.py` (simulador de barreras/bootstrap — Bloque B), las hipótesis reales H001–H005, y todo el Flujo 2 (investigación, agentes, n8n, arXiv).

## Capabilities

### New Capabilities
- `data-pipeline`: Ingesta y limpieza de datos crudos a parquet validado, con reporte de calidad por instrumento; `data/raw/` es inmutable.
- `signal-contract`: Contrato de funciones puras precios → pesos objetivo, con invariantes verificables y una señal de referencia (buy & hold).
- `backtest-engine`: Motor que traduce pesos objetivo en retornos netos aplicando costos; único módulo que aplica costos; verificado contra un Sharpe histórico conocido.
- `reporting`: Generación reproducible de un reporte de desempeño (equity curve, Sharpe, max DD, distribución) desde un solo comando.

### Modified Capabilities
<!-- Ninguna: el repositorio no tiene specs previas. -->

## Impact

- **Estructura nueva**: `data/{raw,clean}/`, `src/{loaders,signals,engine,report,challenge}.py`, `hypotheses/`, `notebooks/`, `results/`, `tests/`.
- **Tooling nuevo**: `pyproject.toml` gestionado con `uv`; dependencias `pandas`, `numpy` (opcional `polars`); Python 3.14.
- **Datos**: requiere descargar dumps diarios EOD de Dukascopy (2005→hoy) para 10 instrumentos: EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, XAUUSD, SPX500, NAS100, GER40, UK100.
- **Sin dependencias externas de red en runtime**: la descarga de datos es un paso manual/previo; el pipeline opera sobre archivos locales.
- **Reglas duras heredadas del documento**: `data/raw/` inmutable, `signals.py` puro, `engine.py` como único punto de costos.
