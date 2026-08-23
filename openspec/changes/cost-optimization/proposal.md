## Why

El suelo de costes (Bloque A) no es necesariamente fijo. Dos palancas sin medir: gross exposure y horizonte de holding. Caracterizarlas para cerrar `docs/cost_floor.md` con el perfil de estrategia que mejor supera el suelo — criterio de selección de la próxima hipótesis.

## Regla

Esto **caracteriza el motor de costes, NO es un nuevo intento de H001/H007**: no toca veredictos ni `intentos_familia_trend`.

## What Changes

- **`scripts/cost_levers.py`** (nuevo) + sección Bloque B en **`docs/cost_floor.md`**:
  - **B.1 barrido de gross** [0.5, 2.5]: bruto y neto vs gross.
  - **B.2 barrido de holding** (mensual/bimestral/trimestral): turnover, margen, spread, neto.

## Hallazgo — ambas expectativas REFUTADAS; el suelo es margen-dominado e irreducible

- **B.1: el gross NO es palanca.** Bruto Y neto son planos (0.229 / −0.145) en todo [0.5, 2.5]. La expectativa del reviewer (neto con máximo interior) se refuta: margen, spread, carry, retorno y vol escalan TODOS con gross → `neto = bruto − coste/vol` es invariante al escalado.
- **B.2: el holding sólo recorta el spread.** El margen es invariante al holding (~2.2%, se paga cada día mantenido); alargar el rebalanceo baja el spread (0.16→0.10%, ~0.06%, despreciable) y el neto empeora (señal stale).

**Respuesta combinada (cierre de `docs/cost_floor.md`):** el suelo lo domina el margen (∝ gross-promedio-sobre-todos-los-días × 261), irreducible para una estrategia siempre-en-mercado. El perfil que mejor lo supera NO es más gross ni holding más largo, sino: (1) **edge bruto > 0.64**, y/o (2) **duty cycle bajo** (flat la mayor parte del tiempo → margen ∝ fracción de días en posición; TOM pagaba ~1/5 por estar flat el 81%). Este perfil pasa a ser criterio de selección POR ENCIMA del orden de la cola.

## Capabilities

### New/Modified Capabilities
<!-- Ninguna: caracterización + doc. skip_specs=true. -->

## Impact

- **Código**: `scripts/cost_levers.py`. **Docs**: `docs/cost_floor.md` (sección Bloque B + respuesta combinada).
- Sin cambios a fichas/veredictos/intentos. Define el criterio de selección de la próxima hipótesis.
