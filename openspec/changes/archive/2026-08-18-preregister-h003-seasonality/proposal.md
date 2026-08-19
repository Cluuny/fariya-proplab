## Why

H001 (trend) quedó muerta; toca la siguiente hipótesis de la cola. Respetando el listado del documento maestro (§2.5, "las seis familias operables"), **H003 = familia 3 = Estacionalidad y efectos de calendario** (mecanismo: flujos institucionales / restricciones de mandato). El protocolo §3.5 exige pre-registrar la ficha con su FALSADOR **antes de una sola línea de señal**. Este change escribe SÓLO la ficha `hypotheses/H003_seasonality.yaml`.

Se aplican las lecciones de H001: (a) turnover bajo —el efecto turn-of-the-month tiene ~4 días de holding al mes, el mejor perfil de costo disponible; (b) expectativa comprometida por Grinold-Kahn; (c) max DD/vol como diagnóstico de primera línea; (d) **esta vez se RESPETA el holdout sagrado** (H001 fue exención por replicación; a partir de aquí la política se ejerce).

## What Changes

- Se crea `hypotheses/H003_seasonality.yaml`: pre-registro del efecto **turn-of-the-month (TOM)** en índices de renta variable (Ariel 1987; McConnell & Xu 2008). Regla: largo en cada índice sólo en la ventana [último día hábil del mes, +3 días hábiles], flat el resto. Universo: SPX500, GER40, JPN225 (el efecto es institucional-equity). Sizing vol-inversa ex-ante a 8% de vol de portafolio (misma infra que H001), bruto ≤ MAX_GROSS.
- **Holdout RESPETADO**: in-sample 2011-09 → 2023-08-16; holdout sagrado 2023-08-17 → 2026 reservado (un solo vistazo para confirmar si pasa in-sample).
- `resultado_esperado` con derivación Grinold-Kahn (universo delgado de 3 índices correlacionados → breadth baja → central ~0.35) y dirección por desviación.
- `FALSADOR`: Sharpe neto in-sample < 0.2 → muerta, sin variantes.
- Diagnósticos requeridos: `turnover_anual`, `sharpe_zero_cost`, max DD/vol.

Fuera de alcance (change SEPARADO posterior): implementar la señal, correr el backtest, tocar el holdout.

## Capabilities

### New/Modified Capabilities
<!-- Ninguna: artefacto de proyecto (ficha YAML). skip_specs=true. -->

## Impact

- **Artefacto nuevo**: `hypotheses/H003_seasonality.yaml` (`estado: pre_registrado`).
- **Sin código ni spec.** No corre backtests ni toca el holdout.
- Actualiza `hypotheses/QUEUE.md` (H003 activa, pre-registrada).
