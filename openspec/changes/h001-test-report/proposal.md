## Why

El runner de H001 (`scripts/run_h001.py`) computó el veredicto pero **sólo lo imprimió a stdout**; no dejó un reporte persistido. El veredicto quedó en la ficha YAML, pero no hay un artefacto de reporte de la prueba —legible, diffable, reproducible— como sí existe para desempeño de estrategias (`src/report.py::generate` → `results/<name>/report.md`) y para calidad de datos (`data/quality_report.md`). Una prueba de hipótesis debe dejar reporte.

## What Changes

- `scripts/run_h001.py` genera y escribe `results/H001/report.md` (determinista, sin timestamps), reutilizando la capa `src/report.py`. Contiene: veredicto, contrato congelado (umbrales), tabla Sharpe neto por muestra × swap, interpretación (regla de dos muestras, caveat de sensibilidad al swap, costo dominante), y el detalle por muestra sobre la especificación primaria (métricas, equity muestreada, max drawdown, distribución de retornos).
- El runner sigue imprimiendo el resumen a stdout y ahora reporta la ruta escrita.

Fuera de alcance: cambiar la señal, el veredicto o el contrato (congelados). Es puramente el reporte que faltaba.

## Capabilities

### New Capabilities
<!-- Ninguna: aplica la capability `reporting` existente a H001. skip_specs=true. -->

### Modified Capabilities
<!-- Ninguna: no cambia el contrato de reporting. -->

## Impact

- **Código**: `scripts/run_h001.py` (añade generación de reporte).
- **Artefacto nuevo**: `results/H001/report.md` (bajo `results/`, gitignoreado como el resto de resultados reproducibles; se regenera con `uv run python scripts/run_h001.py`).
- **Sin cambio de veredicto**: los números son idénticos; sólo se persisten.
