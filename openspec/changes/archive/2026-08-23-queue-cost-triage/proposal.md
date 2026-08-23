## Why

El Bloque B estableció que el suelo lo domina el margen, proporcional al DUTY CYCLE. Ese es ahora el criterio de admisión, por encima del orden de la cola. Hay que aplicar el filtro #6 FORMALMENTE a toda la cola viva y registrar cuántas hipótesis mueren sin correrse.

## What Changes

- **`costs_model.sharpe_bruto_requerido_duty(duty)`** = `0.24·duty + 0.40` (duty 100%→0.64, 50%→0.52, 20%→0.45, 10%→0.42), con la TRAMPA documentada: el bruto whole-series de una estrategia de duty bajo se diluye (`Sharpe_whole ≈ Sharpe_activo·√duty`), así que el ahorro de margen no es magia.
- **`docs/queue_triage.md`**: tabla por hipótesis (duty, turnover, bruto requerido, bruto plausible, veredicto ADMITIDA/RECHAZADA-POR-COSTE) + cuántas mueren.
- **QUEUE.md** actualizado con los estados.

## Resultado

- **H002 (carry) — RECHAZADA-POR-COSTE.** Duty 100% → requerido 0.64; bruto MEDIDO 0.495 (spot+carry), neto 0.282 (el mejor del proyecto, pero corto). Concentración short-JPY (N_eff 3.41; carry = compensación por crash → engañoso para P(pasar)).
- **H005 — RECHAZADA-POR-COSTE** (requerido ~0.78 vs plausible 0.3-0.5).
- **H006 — RECHAZADA-POR-COSTE** (price-based, duty 100%, sin evidencia de bruto ≥0.64).
- H004 y AMT/volume profile: fuera por DATOS.

**Las tres price-based vivas mueren por el filtro #6.** Resultado estructural: todo lo price-based sobre nuestro setup EOD/high-duty muere en el suelo. El camino que queda es una fuente NO-de-precio y de bajo duty → COT (Bloque 2).

## Capabilities

### New/Modified Capabilities
<!-- Ninguna: función de decisión + triaje. skip_specs=true. -->

## Impact

- `src/costs_model.py` (+duty), `tests/test_costs_model.py` (+1), `docs/queue_triage.md`, `hypotheses/QUEUE.md`. Sin correr ni pre-registrar nada.
