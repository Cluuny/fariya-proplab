## Why

El universo actual (9 instrumentos) está dominado por el factor USD (5 de 9 son majors USD) y no tiene rates ni suficiente diversificación geográfica. El plan (Bloque 1) pide auditar qué tiene Dukascopy que no usamos, con el MISMO criterio que mató a Brent (días hábiles faltantes), para decidir a qué instrumentos expandir y qué gaps son estructurales (argumento para datos pagos).

## What Changes

- **`scripts/audit_universe.py`** (nuevo): audita la cobertura real de un directorio de CSVs d1 de dukascopy-node. Por instrumento: rango, obs, días hábiles faltantes, miss% (full y ventana 2015+), barras/año, staleness, veredicto PASS/CAUTION/KILL con el umbral de Brent (>25% = KILL). Reproducible.
- **`data/universe_audit.md`** (nuevo, el entregable): cobertura real de 29 candidatos (cruces FX, metales, energía, más índices, renta fija) + respuestas a las preguntas críticas del plan y la recomendación de universo.

Hallazgos clave (verificados con datos reales):
- **Renta fija**: los CFDs existen (`ustbondtrusd`, `bundtreur`, `ukgilttrgbp`) pero la cobertura diaria es inusable (US T-bond sólo 2019-2023 y detenido; Bund 52% faltante; UK Gilt sin datos) → **gap estructural, argumento para datos pagos de futuros**.
- **WTI = mismo problema que Brent** (25.8% faltante): la energía es estructuralmente esparsa en Dukascopy daily, no era específico de Brent.
- **Cruces FX = la gran ganancia** (audjpy/eurjpy/gbpjpy/euraud/gbpaud/eurchf, 0-10% en 2015+): decorrelacionan del factor USD.
- **Índices**: Dow y Hang Seng limpios+al día; CAC/IBEX/EuroStoxx/FTSE/ASX/Russell con el feed detenido a fin 2024/2025 (research-only).
- Universo operable en vivo pasa de **9 → ~18**; los 25-30 del plan no se alcanzan limpios+live por los gaps de rates/energía.

Fuera de alcance: descargar el universo definitivo a `data/`, tocar `config.py`, correlaciones/breadth (Bloque 2).

## Capabilities

### New/Modified Capabilities
<!-- Ninguna: script de auditoría + artefacto de decisión. skip_specs=true. -->

## Impact

- **Código**: `scripts/audit_universe.py` (nuevo, reutilizable en Bloque 2).
- **Artefacto**: `data/universe_audit.md` (entregable de Bloque 1).
- **Sin cambios de config ni de universo todavía.** Habilita Bloque 2 (ingesta + validación + amplitud efectiva).
