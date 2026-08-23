# Plan del mes de Norgate — escrito antes de contratar

## Por qué

El GO de futuros es frágil y el plan implícito actual (reconstruir N_eff con continuos
reales) sólo re-verifica el criterio (2) — amplitud — que NO es el número que decide. El
número que decide la opción A es el **bruto de exceso de trend sobre el universo REAL de
futuros** contra el listón de coste recalculado (0.424). Hoy la mejor evidencia propia
(H007-A 0.370) está a 0.22 SE del listón — indistinguible. Antes de gastar el mes de datos
hay que fijar por escrito qué se corre y qué criterio decide, para que el resultado no se
reinterprete a conveniencia.

## Qué cambia

- Se escribe `docs/futures_month_plan.md` con:
  - El diagnóstico: `signals.tsmom` **sin modificar** sobre ~25–30 futuros líquidos
    (rates+índices+FX+energía+metales; agrícolas y NG excluidos por coste de roll).
  - Su naturaleza: **diagnóstico**, no hipótesis (sin pre-registro, sin consumir cola, sin
    tocar el holdout, señal intacta).
  - Los tres números en orden: (1) bruto de exceso con IC 95% block-bootstrap, (2) N_eff con
    continuos reales, (3) coste de roll medido.
  - El **criterio de decisión comprometido**: >0.42 IC sin cruzar → GO; <0.42 IC sin cruzar
    → opción A CERRADA POR EVIDENCIA; IC cruza → INDETERMINADO (y entonces: los futuros
    resuelven coste, no edge).
  - La **expectativa comprometida**: bruto 0.30–0.45, IC cruza → resultado más probable
    INDETERMINADO.
  - El **plan de ejecución**: descargas día 0, qué corre día 1, deadline de cancelación.

## Impacto

- Docs only: `docs/futures_month_plan.md` (nuevo). Sin código, sin datos, sin delta de spec.
- NO se contrata Norgate en este change — el plan es el prerequisito para hacerlo.
