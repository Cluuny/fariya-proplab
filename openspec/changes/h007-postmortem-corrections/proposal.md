## Why

Dos conclusiones del reporte de H007 no se sostienen. Corregir el **registro post-ejecución** (veredicto/resultado) SIN tocar FALSADOR ni resultado_esperado (congelados al correr).

## What Changes

- **(1.1) Calibración del marco → UNDERPOWERED**, no "dirección correcta". El test no tenía poder: la diferencia H007−H001 (period-matched, portafolios con ρ~0.85) está a ~1 SE en ambas muestras (A Δ+0.17, SE 0.13, t=1.34; B Δ+0.20, SE 0.19, t=1.02) → indistinguible de ruido. El test **no pudo resolver** si el marco predice → NO se usa para la decisión de datos de futuros, ni como estimación puntual NI como dirección. Y la lectura previa "la amplitud ayudó MÁS de lo predicho" tiene una explicación más simple: 6 de los 8 añadidos son recombinaciones lineales sin información nueva y no pueden producir un salto de ~7.6× en IR; cuando lo medido excede lo que la teoría permite, el default es RUIDO.
- **(1.2) Muestra A → veredicto DEPENDIENTE DEL PLACEHOLDER**, no falsación limpia. A cruza el falsador con el swap (0.0→+0.354 VIVA; 0.3→+0.184 muerta; 1.0→−0.212) → se invoca la cláusula: "muerta bajo la especificación primaria, PERO el veredicto es sobre el placeholder de swap, no sobre la estrategia". Muestra B sí muere limpia (0.211 a swap 0.0 ya es marginal; 0.040 a 0.3 muere sin depender del placeholder).

Cambios en `scripts/run_h007.py` (cómputo de SE de la diferencia + t, y lógica de dependencia del placeholder), regeneración de `results/H007/report.md`, y el bloque `veredicto` de `hypotheses/H007_tsmom_expanded.yaml`.

## Capabilities

### New/Modified Capabilities
<!-- Ninguna: corrección de registro post-ejecución + reporte. skip_specs=true. -->

## Impact

- **Código**: `scripts/run_h007.py` (SE de la diferencia, poder, dependencia del placeholder).
- **Artefactos**: `results/H007/report.md`, `veredicto` en la ficha, `QUEUE.md`. FALSADOR/resultado_esperado NO tocados.
- Corrige el registro: la corrida quedó UNDERPOWERED para el marco; H007 muerta (B limpia, A sobre el placeholder).
