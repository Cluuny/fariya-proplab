## Why

La expansión de universo dejó dos lecciones que se olvidan y se vuelven a pagar (los cruces FX no aportan información; N_eff sobreestima la ganancia), más una estimación revisada para la decisión de datos de futuros (la previa falló 35%). Documentarlas para que informen decisiones futuras.

## What Changes

- **`docs/breadth-lessons.md`** (nuevo): 
  1. Los cruces FX son recombinaciones de los majors (`log(EURJPY)=log(EURUSD)+log(USDJPY)`) → cero información nueva; sólo EURCHF, HK50 y plata aportaron de verdad.
  2. Limitación de N_eff: puede subir con combinaciones lineales sin información → el +1.6 medido sobreestima la ganancia; test de construibilidad ANTES de mirar N_eff.
  3. Estimación revisada para datos de futuros: la previa (N_eff 7→12-13, ×1.8) estaba inflada (predijo 7, midió 5.32); revisada a ~8-9 y ×1.25-1.30 — incremento, no desbloqueo, pero única vía a rates/commodities (donde la industria atribuye el trend).

## Capabilities

### New/Modified Capabilities
<!-- Ninguna: documentación. skip_specs=true. -->

## Impact

- **Artefacto**: `docs/breadth-lessons.md`. Sin código.
- Informa decisiones futuras de universo y la decisión de pagar por datos.
