## Why

Cuatro mediciones (H001-A/B, H007-A/B) dicen que el bruto de trend vive en 0.23-0.37 y que los costes se comen ~88% del bruto. Hay que convertir eso en una herramienta de decisión (un filtro previo a correr), no dejarlo como observación.

## What Changes

- **`src/costs_model.py`** (nuevo): descomposición del coste anual (margen `0.42bp×gross×261`, spread `1.5bp×turnover`, carry `E[carry·w]`) calibrada a lo medido, y `sharpe_bruto_requerido(vol, gross, turnover, umbral)`. Con los parámetros actuales: break-even 0.24, requerido (net 0.4) **0.64** — el trend real (0.23-0.37) queda estructuralmente por debajo.
- **`docs/cost_floor.md`** (nuevo): A.1 descomposición medida (margen ~92% del coste), A.2 Sharpe bruto requerido, A.3 **filtro de admisión #6** (estimar gross/turnover y bruto requerido ANTES de correr; descartar si excede lo que la literatura reporta), A.4 **cribado de H002**.
- **Filtro #6 aplicado retroactivamente** (QUEUE): H005 (reversión, turnover 50-100× → ~1.1%/año solo spread, requerido ~0.78) queda **en riesgo por filtro #6**; H002 pasa.
- **`tests/test_costs_model.py`** (+4).

## Hallazgo — cribado de H002 (A.4): expectativa comprometida REFUTADA

Expectativa escrita antes de correr: "el carry no supera el margen, H002 no pasa". Resultado real: el portafolio de carry estático (long top-3/short bottom-3, vol-inversa) tiene **E[carry·w] +2.17%/año vs margen 1.10%/año → carry ~2× el margen** (ratio invariante al escalado). **H002 SÍ pasa el cribado** — no muere por aritmética. Caveats registrados: concentración short-JPY (~1-2 apuestas independientes, N_eff FX 3.41), y el Sharpe del componente spot es +0.065 (riesgo de crash del carry). H002 merece pre-registro formal; H005 no.

## Capabilities

### New/Modified Capabilities
<!-- Ninguna: herramienta de decisión + doc de protocolo. skip_specs=true. -->

## Impact

- **Código**: `src/costs_model.py`, `tests/test_costs_model.py`. **Docs**: `docs/cost_floor.md`, `hypotheses/QUEUE.md`.
- El filtro #6 pasa a ser criterio de admisión; el perfil de estrategia óptimo se cierra en el Bloque B (gross/turnover/holding).
