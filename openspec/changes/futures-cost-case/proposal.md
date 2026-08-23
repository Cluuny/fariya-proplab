## Why

Antes de gastar en datos de futuros: ¿el cambio de vehículo baja el suelo de costes lo suficiente para que un bruto realista sobreviva? Responder con aritmética y datos gratis. Criterio comprometido (docs/futures_case.md): suscripción justificada SÓLO si (1) bruto requerido < 0.50 Y (2) N_eff > 7.5; si no, opción A cerrada por evidencia.

## What Changes

- **`docs/futures_case.md`**: criterio de decisión comprometido + sección de costes (Bloque 1).
- Hecho estructural: los futuros NO cobran el margen diario de financiación que domina el suelo del CFD (0.42 bp/día ≈ 1.96%/año). Coste = roll (4/año) + comisión + spread, sin margen.
- Fuentes públicas documentadas (CME specs; IBKR $0.85/lado ~$4.20 round-trip). Coste de mantener por mercado (~25 mercados); ags/natgas caros por roll (marcados NO).
- Suelo recalculado con `costs_model`: libro líquido 0.19%/año → **bruto requerido 0.66 → 0.424** → **criterio (1) SE CUMPLE**. H007-A (0.370) queda corto por −0.054 (vs −0.29 en CFD).

## Capabilities

### New/Modified Capabilities
<!-- Ninguna: análisis + doc. skip_specs=true. -->

## Impact

- `docs/futures_case.md` (nuevo, sección costes). Sin código. Falta el criterio (2) — amplitud (Bloque 2).
