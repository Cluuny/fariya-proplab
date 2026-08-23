## Why

Con el universo ampliado a 17, toca la segunda mirada al efecto de trend (H001 murió sobre 9). H007 NO es caza de variantes: la ampliación se justificó por un argumento EXTERNO (la industria atribuye los retornos de trend a renta fija y materias primas; el universo no las tenía), independiente de H001. La señal `tsmom` no se modifica. Protocolo §3.5: pre-registrar la ficha con su FALSADOR antes de una sola corrida. Este change escribe SÓLO la ficha.

El punto real de H007 no es "quizá ahora sí gane" (se espera que muera): es **calibrar el marco** de amplitud efectiva/Grinold-Kahn, que acaba de fallar ~35% en su primera predicción verificable (predijo N_eff 7, midió 5.32). H007 lo testea con coste casi nulo (señal + runner ya existen).

## What Changes

- Se crea `hypotheses/H007_tsmom_expanded.yaml` (esquema §7.1, mismo rigor que H001/H003):
  - `familia: trend`, señal `tsmom` sin modificar, universo de 17, dos muestras ajustadas a la cobertura real (A: FX+metales 2005-2026 con 2008; B: los 17, 2015-2026).
  - `relacion_con_H001` (segunda mirada, justificación externa), `intentos_familia_trend: 3` (para el deflated Sharpe).
  - `resultado_esperado`: bruto [0.29, 0.36] (H001 × 1.18 por N_eff), neto [0.12, 0.20], veredicto esperado muerta.
  - `FALSADOR` = el de H001 (Sharpe neto < 0.2 → muerta).
  - **`calibracion_del_marco`** (campo nuevo, el punto real): si el Sharpe BRUTO cae en [0.25, 0.40] el marco es predictivo y se usa para la decisión de datos de futuros; si cae fuera, no se gasta dinero apoyándose en él. Independiente del FALSADOR.
  - `holdout: exento` (idéntico a H001: replicación exacta, sin tuneo).
- `hypotheses/QUEUE.md`: H007 pre-registrada.

Fuera de alcance (explícito): NO implementar, NO correr. La ficha se revisa antes.

## Capabilities

### New/Modified Capabilities
<!-- Ninguna: ficha de pre-registro (artefacto). skip_specs=true. -->

## Impact

- **Artefacto nuevo**: `hypotheses/H007_tsmom_expanded.yaml` (`pre_registrado`), `QUEUE.md` actualizado.
- **Sin código ni corridas.** Habilita el change de implementación posterior (reusa `tsmom` + un runner tipo `run_h001`/`run_h003` sobre el universo 17), tras revisión de la ficha.
