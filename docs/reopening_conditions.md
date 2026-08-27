# Condiciones de reapertura del programa

El programa está CERRADO (`docs/program_verdict.md`): nueve familias, cero supervivientes, y
—medido de raíz— ningún terreno accesible con la amplitud para despejar el listón. Este documento
es **lo único que deja la puerta abierta.** El programa se reabre ÚNICAMENTE si se cumple una de
las tres condiciones OBJETIVAS de abajo. **Cualquier reapertura debe citar cuál se cumplió, con el
número medido.** No vale «creo que esta vez sí».

## Las tres condiciones (basta UNA, con el número)

### C1 — Amplitud: acceso a un universo con N_eff medido ≥ 14

El cierre por amplitud (`docs/terrain_breadth.md`) mostró que superar el listón 0.64 con un IC
plausible (0.05) exige **N_eff ≥ 14**, y ningún universo accesible llega (el máximo, futuros
proxy, es 8.15; cripto gratis es 2.16). Reapertura válida si se accede a un universo cuyo N_eff
**medido** (autovalores de la matriz de correlación de retornos, `scripts/terrain_breadth.py` /
`scripts/effective_breadth.py`, no estimado con proxies) sea **≥ 14**, y esté dentro del
presupuesto de datos vigente. Citar: universo, N_eff medido, coste $/mes, ventana de datos.

### C2 — Objetivo: revisión a la baja del listón, recalculada y aceptada explícitamente

El cierre es relativo al objetivo comprometido de **0.40 neto** (→ listón 0.64 CFD / 0.65 cripto /
0.96 a duty 31%). Con la mitad de ambición (p. ej. 0.20 neto → listón ~0.44) algún universo
rozaría (futuros mensual a IC 0.05 = 0.49). Reapertura válida si el operador **revisa el objetivo
a la baja de forma explícita y comprometida**, recalcula el listón con el modelo de costes vigente
(`src/costs_model.py`), y **acepta el nuevo objetivo por escrito** (no como excusa post-hoc para
un backtest). Citar: nuevo objetivo neto, listón recalculado, y que la aceptación es previa, no
posterior al resultado.

### C3 — Señal: evidencia de un IC ≥ 0.10 en algún efecto, MEDIDO, no supuesto

El techo de IR = IC·√N_eff. Con N_eff ~8 (futuros) un **IC ≥ 0.10** lleva el techo mensual por
encima del listón. El programa NUNCA produjo señal cerca de eso (OFI ~0, H008 negativo, carry el
mejor a 0.495 bruto ya limitado por amplitud). Reapertura válida si se **mide** un IC ≥ 0.10
(correlación forecast-retorno realizado al horizonte de rebalanceo) en un efecto operable,
**out-of-sample**, con intervalo de confianza que no cruce 0.10 por abajo. Citar: efecto,
horizonte, IC medido con IC95, y la muestra out-of-sample.

## Lo que NO es una condición de reapertura

- Un backtest con Sharpe alto SIN deflactar (el cribado aritmético lo cierra — ver Sectoral
  Momentum, `docs/candidate_sectoral_screen.md`).
- Más volumen de candidatos de la misma calidad (91 produjeron cero que sobrevivan el cribado).
- Una corazonada, una familia «nueva» por intuición, o «el mercado cambió».
- Un IC o un N_eff ESTIMADO con proxies o supuesto — sólo cuenta lo MEDIDO.

## Procedimiento

Una reapertura empieza con un documento `docs/reopening_<fecha>.md` que (1) cita C1, C2 o C3 con
el número medido y su fuente, (2) enlaza los datos/script que lo producen, y (3) sólo entonces
entra al pipeline de investigación (Flujo 2) con su falsador pre-registrado. Sin ese documento y
su número, el programa sigue cerrado.
