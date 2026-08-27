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

### C2 — Señal: evidencia de un IC ≥ 0.10 en algún efecto, MEDIDO, no supuesto

El techo de IR = IC·√BR. Con N_eff ~8 (futuros) un **IC ≥ 0.10** lleva el techo mensual por encima
del listón. **El mejor IC IMPLÍCITO que el programa produjo es 0.077** (H002 carry: Sharpe bruto
0.495 / √(N_eff 3.41 × 12 rebalanceos) = 0.077), y H002 murió por concentración; el resto están más
abajo (OFI ~0, H008 negativo). Reapertura válida si se **mide** un IC ≥ 0.10 (correlación
forecast-retorno realizado al horizonte de rebalanceo) en un efecto operable, **out-of-sample**,
con intervalo de confianza que no cruce 0.10 por abajo. Citar: efecto, horizonte, IC medido con
IC95, y la muestra out-of-sample.

### C3 — Objetivo: revisión a la baja del listón, recalculada y aceptada explícitamente

El cierre es relativo al objetivo comprometido de **0.40 neto** (→ listón 0.64 CFD / 0.65 cripto /
0.96 a duty 31%). Bajarlo a **0.20 neto** hace caer el listón a ~0.44 (CFD, duty 1.0), pero **sigue
sin despejar con lo DESPLEGABLE**: trend neto ~0.10 (bruto 0.37), industria 0.32; lo único que
rozaría (carry bruto 0.495) NO es desplegable (concentración short-JPY, N_eff 3.41). Reapertura
válida si el operador **revisa el objetivo a la baja de forma explícita y comprometida**, recalcula
el listón con el modelo de costes vigente (`src/costs_model.py`), **acepta el nuevo objetivo por
escrito** (no post-hoc), Y a ese objetivo revisado algo DESPLEGABLE despeja. Citar: nuevo objetivo
neto, listón recalculado, la aceptación previa, y qué estrategia desplegable lo supera.

## Lo que NO es una condición de reapertura

- Un backtest con Sharpe alto SIN deflactar (el cribado aritmético lo cierra — ver Sectoral
  Momentum, `docs/candidate_sectoral_screen.md`).
- Más volumen de candidatos de la misma calidad (91 produjeron cero que sobrevivan el cribado).
- Una corazonada, una familia «nueva» por intuición, o «el mercado cambió».
- Un IC o un N_eff ESTIMADO con proxies o supuesto — sólo cuenta lo MEDIDO.

## Estado HOY — ninguna condición se cumple, con el número (2026-08-27)

| condición | umbral | medido hoy | ¿se cumple? |
|---|---|---|---|
| **C1** amplitud | N_eff medido ≥ 14 | **8.15** (futuros, el más ancho accesible; cripto gratis 2.16) | **NO** |
| **C2** señal (IC) | IC ≥ 0.10 medido out-of-sample | **0.077** (mejor implícito, H002 = 0.495/√(3.41·12)); resto más abajo | **NO** |
| **C3** objetivo | revisado a la baja Y algo desplegable despeja | bajado a **0.20** → listón ~0.44; nada desplegable despeja (carry 0.495 no desplegable) | **NO** |

**Ninguna de las tres se cumple hoy. El programa permanece CERRADO.** Para reabrir hay que mover
uno de estos tres números por encima de su umbral y citarlo — no reinterpretar los existentes.

## Procedimiento

Una reapertura empieza con un documento `docs/reopening_<fecha>.md` que (1) cita C1, C2 o C3 con
el número medido y su fuente, (2) enlaza los datos/script que lo producen, y (3) sólo entonces
entra al pipeline de investigación (Flujo 2) con su falsador pre-registrado. Sin ese documento y
su número, el programa sigue cerrado.
