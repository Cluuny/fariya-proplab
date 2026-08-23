## Why

US30 (Dow) sale del universo activo. **La razón NO es el −0.13 de amplitud efectiva** —ese número está dentro del ruido de la métrica. La razón es de **fricción**: US30 y SPX500 son la MISMA exposición (equity-US large-cap, correlación ~0.95). En una cartera vol-inversa el peso objetivo de esa exposición se reparte entre DOS instrumentos, y se paga **spread dos veces por la misma posición**. Es fricción pura, y H001 demostró que la fricción es exactamente lo que mata los edges débiles (su Sharpe bruto ~0.25 murió neto de costos). Mantener dos representantes de la misma exposición sólo añade coste sin añadir información.

AUDJPY **se queda**: aporta poco (+0.05 a N_eff) pero no cuesta nada mantenerlo, y en una hipótesis de carry el cruce podría importar (diferencial AUD/JPY).

## What Changes

- **`config.INSTRUMENTS` 18 → 17**: se elimina `US30`. Se conserva su mapeo en `DUKASCOPY_SYMBOLS`/`DUKASCOPY_POINT` con nota (como BRENT), por si se re-evalúa.
- **Regenerar** `data/clean` (loaders) + `data/quality_report.md` + `data/universe_expansion.md` con 17.
- Test de universo actualizado (18 → 17).

## Capabilities

### New/Modified Capabilities
<!-- Ninguna: cambio de universo (config). skip_specs=true. -->

## Impact

- **Código**: `src/config.py` (quita US30 de INSTRUMENTS), `tests/test_scaffolding.py`.
- **Artefactos**: se regenera el reporte de amplitud efectiva con 17.
- Sin cambio de comportamiento del motor ni de las señales.
