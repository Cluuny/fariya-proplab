## Why

La ficha de H003 (turn-of-the-month) está pre-registrada y endurecida (falsador relativo al nulo, test de existencia separado del de explotabilidad, poder estadístico). Toca implementar la señal y correr el veredicto **in-sample**, contra el contrato congelado, **sin tocar el holdout** (2023-08-17 → 2026).

## What Changes

- **Nueva señal `tom_seasonal`** en `src/signals.py`: long-only en la ventana TOM [-1, +3] (último día hábil del mes + primeros 3), flat el resto; sizing vol-inversa ex-ante a 8% de vol de portafolio (misma recipe que `tsmom`), bruto ≤ MAX_GROSS. Se factoriza un helper `_long_inverse_vol(prices, active_mask, ...)` para que la señal y el benchmark nulo compartan EXACTAMENTE el mismo constructor de pesos (única diferencia: qué días están activos).
- **Runner `scripts/run_h003.py`** que produce el veredicto in-sample:
  - **Existencia** (`estadistico_primario`): contraste de medias del retorno diario TOM vs no-TOM, por instrumento y agrupado, con IC 95% por block bootstrap.
  - **Explotabilidad**: Sharpe neto de TOM (swap 0.3 primario + 0.0/1.0 sensibilidad) vs el **benchmark nulo** (mismo sizing, mismo nº de días/mes, días ALEATORIOS; 1000 remuestreos semilla fija) → p95.
  - **Poder**: Sharpe con IC 95%; estado `underpowered` si el IC no resuelve.
  - **Diagnósticos** (lección H001): `turnover_anual`, `sharpe_zero_cost`, max DD/vol, y **tripwire de max_gross** (si hay recorte = bug).
  - **Holdout intacto**: todo se computa sobre 2011-09 → 2023-08-16; el runner nunca carga el tramo de holdout.
- **Veredicto escrito a la ficha** (`fecha_test`, `estado`, `resultado`) sin tocar FALSADOR/metrica_exito/resultado_esperado (congelados). Reporte determinista en `results/H003/report.md`.
- **Tests** (`tests/test_tom_seasonal.py`): pureza/forma/determinismo, long-only, activo sólo en ventana TOM (~19% de días), ex-ante (extender con futuro no cambia pesos pasados), tripwire de exposición.

Fuera de alcance: tocar el holdout (sólo se toca si pasa in-sample, en un paso posterior).

## Capabilities

### Modified Capabilities
- `signal-contract`: añade el requisito de la señal TOM estacional (long-only en ventana de calendario, sizing vol-inversa ex-ante).

## Impact

- **Código**: `src/signals.py` (+`tom_seasonal`, `_tom_mask`, `_long_inverse_vol`), `scripts/run_h003.py` (nuevo), `tests/test_tom_seasonal.py` (nuevo).
- **Artefactos**: `hypotheses/H003_seasonality.yaml` recibe el veredicto; `results/H003/report.md` (nuevo). Holdout NO tocado.
- Segundo veredicto del proyecto, esta vez con test falsable relativo al nulo.
