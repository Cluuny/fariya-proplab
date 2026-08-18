## Why

El contrato de H001 (`hypotheses/H001_tsmom.yaml`) está pre-registrado y congelado. Toca **implementar la señal contra el contrato y correr** —el primer test real del sistema completo (datos reales → señal → motor con costos → Sharpe neto → veredicto). El veredicto se juzga contra el FALSADOR y la expectativa comprometida (~0.40), sin editar ninguno.

## What Changes

- **Nueva señal `tsmom`** en `src/signals.py`, función pura conforme al contrato: signo del retorno a 12 meses de calendario (gap-safe) por instrumento → dirección; sizing por vol-inversa (`engine.rolling_vol`) escalado **ex-ante** a ~8% de vol de portafolio (escalar rodante de un paso), bruto ≤ `MAX_GROSS_EXPOSURE`; rebalanceo el primer día hábil del mes con holding entre fechas. Parametrizada por `lookback_months` (12 primario, 6 robustez) y `vol_target`.
- **Runner de veredicto** `scripts/run_h001.py`: carga los parquet limpios, construye las **dos muestras** (A: FX+oro 2004-2026; B: los 9 2015-2026), corre la especificación primaria (swap 0.3 bp) más las dos de sensibilidad (0.0, 1.0), computa Sharpe neto por muestra, aplica la regla de zona marginal (chequeo de robustez + deflated Sharpe si cae en [0.2, 0.4]) y emite el veredicto.
- **Se escribe el veredicto de vuelta a la ficha** (`fecha_test`, `intentos_realizados`, `resultado`, `veredicto`, `estado`) — la única edición legítima post-ejecución (registrar resultados, NO mover el falsador).
- **Tests**: pureza/forma/determinismo de `tsmom`, invariante de exposición, dirección correcta (ret_12m>0 → long), rebalanceo mensual, y que el escalado es ex-ante (no cambia si se le añade data futura).

Fuera de alcance: portafolio multi-hipótesis, H002.

## Capabilities

### Modified Capabilities
- `signal-contract`: añade el requisito de la señal TSMOM (dirección por ret_12m, sizing vol-inversa ex-ante, rebalanceo mensual).

## Impact

- **Código**: `src/signals.py` (+`tsmom` y helper de vol-target), `scripts/run_h001.py` (nuevo), `tests/test_tsmom.py` (nuevo).
- **Artefacto**: `hypotheses/H001_tsmom.yaml` pasa de `pre_registrado` a `testeado`/`viable`/`muerta`/`parked` con el resultado real.
- **Primer veredicto del proyecto.** El contrato congelado se respeta al pie; el número se reporta contra la expectativa de 0.40.
