## Why

Tres correcciones a la ficha de H007 tras revisión, **antes de correr** (sigue `pre_registrado`, `intentos_realizados: 0` → enmienda pre-ejecución legítima).

1. **La exención de holdout ya no se sostiene (importante).** H001 se eximió por ser replicación pura (cero libertad de especificación sobre nuestros datos). H007 sí tiene ese grado de libertad: la selección concreta del universo (estos 17, con US30 fuera) se hizo DESPUÉS de ver morir a H001 y con la amplitud efectiva medida sobre datos propios. Eso es descubrimiento, no replicación (y `HOLDOUT.md` rige desde la primera de descubrimiento). Argumento decisivo: con exención, un H007 que sobreviva no se distinguiría de un artefacto de selección de universo. → **holdout: respetado, in-sample hasta 2023-08-16.**
2. **N_eff con su universo + factor recalculado.** La ficha decía 5.32 sin contexto. Se explicita: 5.32 (17, tras US30), 5.20 (18), 3.73 (9). Y √(5.32/3.73) = **1.194** (no 1.18) → `bruto_esperado` [0.29, **0.37**].
3. **Convención de conteo (menor).** Se mantiene `intentos_familia_trend: 3` (conservador) y se anota: las dos muestras de H007 suman 2 → la familia queda en **5 tras esta corrida**; el deflated Sharpe usa N=5.

## What Changes

- `hypotheses/H007_tsmom_expanded.yaml`: `holdout: respetado` + `holdout_detalle` + `holdout_razon` reescrita; muestras A/B cortadas en 2023-08-16; `metrica_exito`/`FALSADOR` in-sample; `n_eff` explícito; `bruto_esperado` [0.29, 0.37] con factor 1.194; `intentos_familia_convencion` (N=5); `enmiendas` (pre-ejecución).
- `hypotheses/QUEUE.md`: nota de H007 actualizada (holdout respetado).

Fuera de alcance: implementar/correr (la ficha corregida se puede implementar ya).

## Capabilities

### New/Modified Capabilities
<!-- Ninguna: enmienda de ficha (pre-ejecución). skip_specs=true. -->

## Impact

- **Artefacto**: `hypotheses/H007_tsmom_expanded.yaml` (sigue `pre_registrado`). Holdout ahora protegido: si H007 sobrevive contra pronóstico, se podrá confirmar sin ambigüedad.
- Sin código.
