# Plan del mes de Norgate — UNA pregunta, comprometida antes de contratar

Este documento se escribe **ANTES de suscribir** el mes de datos de futuros. Fija qué se
corre, qué números decide, y el criterio de decisión — todo committeado por adelantado
para que el resultado no se pueda reinterpretar a conveniencia.

## Por qué el plan anterior apuntaba al número equivocado

El plan implícito en `docs/futures_case.md` (reconstruir N_eff con continuos reales) sólo
re-verifica el **criterio (2) — amplitud**. Pero (2) no es el número que decide. En el
veredicto GO frágil, (2) pasa por 0.18 sobre un techo optimista; aun si se confirmara,
**el edge sigue sin resolver**. El número que decide la opción A es el otro:

> **¿Produce el universo REAL de futuros un bruto de trend ≥ 0.424 (el listón de coste
> recalculado)?**

Hoy, la mejor evidencia propia es H007-A **bruto 0.370** (universo CFD FX+metales). Contra
0.424 está corto por **0.054 ≈ 0.22 SE** — estadísticamente **indistinguible** del listón.
El mes de datos existe para medir ESE número sobre el universo correcto, no para pulir la
amplitud. Si el bruto real no supera el listón, un N_eff bonito no salva nada.

## Qué se corre (2.1) — el diagnóstico

- **Señal:** `signals.tsmom` **sin modificar** (misma regla ret_12m, mismo sizing
  inverso-vol a ~8% vol de portafolio). No se toca la señal — si se tunea, deja de ser
  medición y pasa a ser overfitting.
- **Universo:** ~25–30 mercados de futuros líquidos con continuos ajustados por roll:
  - **Rates:** ZT, ZF, ZN (ZB excluido — roll caro, tick grande).
  - **Índices:** ES, NQ, YM, RTY.
  - **FX:** 6E, 6J, 6B, 6A, 6C (6A/6C marginales por roll, se incluyen para amplitud).
  - **Energía:** CL, RB, HO (NG **excluido** — roll 0.50%/año).
  - **Metales:** GC, SI, HG.
  - **Agrícolas: EXCLUIDOS** (ZC/ZW/SB/ZS roll 0.5–0.9%/año — no valen por coste, ya
    documentado en `futures_case.md` Bloque 1).
  - La selección es por **coste de roll bajo**, decidida por adelantado, no por resultado.

## Qué NO es (2.2) — es un DIAGNÓSTICO, no una hipótesis

- **NO** hay pre-registro nuevo (ficha `hypotheses/*.yaml`), **NO** consume intento de
  cola, **NO** toca el holdout sagrado. H001/H007 ya falsaron TSMOM como hipótesis; esto
  mide el mismo efecto conocido sobre un universo nuevo para decidir el **vehículo**, no
  para descubrir edge.
- **NO** se optimiza nada: mismo lookback, mismo sizing, mismo umbral. Un solo run.
- El único output es de medición: los cuatro números de abajo (1b decide).

## El test de NIVEL no puede discriminar — por qué hace falta un segundo número

El criterio de nivel (bruto de futuros vs umbral 0.42) tiene un IC tan ancho que su
resultado se conoce de antemano. Con el SE del bruto (~0.240):

    0.370 ± 1.96 × 0.240 = [−0.10, +0.84]

Para que ese IC **no** cruce 0.42 haría falta un bruto medido por encima de **~0.85** o
por debajo de **~0.0** — ambos extremos improbables dado todo lo medido (H007-A 0.370,
industria ~0.32 bruto). **El resultado INDETERMINADO no es "probable": es prácticamente
SEGURO POR CONSTRUCCIÓN DEL TEST.** Un test cuyo veredicto se sabe antes de correrlo NO
justifica el gasto por sí solo. Por eso el mes se justifica con el número **1b**, que sí
discrimina.

## Los cuatro números, EN ORDEN (2.3)

**1b — Δ bruto contra NUESTRO PROPIO CFD (EL QUE DECIDE).** En vez de medir el bruto de
futuros contra un umbral, medirlo contra nuestro propio bruto de CFD sobre el **mismo
período**. Los dos portafolios comparten instrumentos (FX y metales están en ambos) →
correlación ~0.7–0.8 → el SE de la DIFERENCIA colapsa:

    Δ bruto = bruto(futuros, universo completo) − bruto(CFD, MISMO período, mismas fechas)
    SE(Δ) ≈ 0.24 × √(2(1−0.75)) ≈ 0.17   (vs 0.24 del nivel)

- **IC 95% de la DIFERENCIA por bootstrap PAREADO por bloques** (mismas fechas en ambas
  series, bloques ~21 días).
- **Ventana solapada EXACTA:** recortar ambos paneles al período común ANTES de comparar.
  Reportar qué período es y cuántos años cubre.
- La pregunta que 1b SÍ puede responder es la pregunta económica real de la opción A:
  **¿añadir rates, energía y metales industriales (HG) sube el bruto de trend de forma
  medible?**

  | resultado 1b | decisión |
  |---|---|
  | **Δ > +0.15**, IC no cruza 0 | las clases nuevas (rates, energía, HG) **APORTAN** → el vehículo vale lo que cuesta |
  | **Δ ≈ 0**, IC no cruza 0 | rates y energía **no aportan** bruto en este período → **opción A muerta por evidencia PROPIA** |
  | IC **cruza 0** | no concluyente sobre el aporte de las clases nuevas |

  **Expectativa comprometida (antes de correr):** Δ entre **+0.05 y +0.20**, con IC que
  probablemente cruza 0 pero **mucho menos ancho** que el del nivel. Es el número con la
  mejor relación información/coste del mes.

**1 — Bruto de exceso de trend vs 0.42 (se reporta, pero será INDETERMINADO).** Con **IC
95% por block bootstrap** (bloques ~21 días). *Nota:* nuestro bruto ya es de exceso (P&L
de precio, sin interés sobre colateral) — comparable directo al 0.42 y al 0.32 de la
industria (ver `docs/futures_case.md`). Por lo dicho arriba, se sabe de antemano que su IC
cruzará 0.42; se reporta por completitud, no decide.

**2 — N_eff** con continuos **reales** (no proxies ETF) — autovalores de la matriz de
correlación del universo operable. Re-verifica el criterio de amplitud con datos reales
(los ETFs inflaban). Soporte, no decide.

**3 — Coste de roll MEDIDO** por mercado (del calendar spread real de los continuos), para
sustituir la estimación de 0.19%/año del Bloque 1 por un número observado. Soporte.

El número **1b es el que decide.** 1 es indeterminado por construcción; 2 y 3 son soporte.

## Criterio de decisión — COMPROMETIDO (2.4)

**El criterio que DECIDE es 1b (Δ vs nuestro propio CFD), no el nivel.** Su tabla de
decisión está arriba en la sección de números (Δ > +0.15 → aportan; Δ ≈ 0 → opción A
muerta por evidencia propia; IC cruza 0 → no concluyente). Ese es el veredicto operativo
del mes.

El criterio de nivel (número 1) se documenta pero se sabe INDETERMINADO por construcción:

| resultado nivel | decisión |
|---|---|
| bruto **> 0.42** y el IC **NO cruza** 0.42 | GO por nivel (improbable — haría falta bruto medido ~0.85+). |
| bruto **< 0.42** y el IC **NO cruza** 0.42 | cierre por nivel (improbable — haría falta bruto ~0.0). |
| el IC **cruza** 0.42 (**resultado esperado, ~seguro**) | **INDETERMINADO por nivel** — y entonces: **los futuros resuelven el COSTE, no el EDGE.** El veredicto real lo da 1b, no esto. |

## Expectativa — COMPROMETIDA antes de correr (2.5)

- **Nivel (número 1):** bruto de exceso **0.30–0.45**, con el **IC cruzando 0.42** →
  INDETERMINADO ~seguro. Base: H007-A 0.370 e industria ~0.32 bruto, ambos al borde de
  0.42 con SE 0.24. Comprometer esto evita leer el indeterminado esperado como un GO.
- **1b (número que decide):** **Δ entre +0.05 y +0.20**, con IC que probablemente cruza 0
  pero mucho más estrecho (SE ~0.17 vs 0.24). Repetido aquí para que quede committeado
  junto al del nivel.

Ambas expectativas se escriben ANTES de correr. Si el resultado difiere, es señal, no
excusa para re-correr con otra configuración.

## Plan de ejecución (2.6)

- **Día 0 (contratar):** suscribir Norgate Futures (~$50, ~1/10 de un challenge). Bajar los
  continuos ajustados por roll (EOD) de los ~25–30 mercados listados.
- **Día 1:** cargar a `data/futures/`, correr `engine.backtest` con `signals.tsmom` sin
  modificar sobre el universo completo. Calcular los cuatro números: **1b (Δ vs CFD, con
  bootstrap pareado sobre la ventana común exacta)**, 1 (nivel + IC), 2 (N_eff real), 3
  (roll medido). Un script de diagnóstico dedicado (`scripts/futures_diagnostic.py`), sin
  pre-registro.
- **Día 2–3:** aplicar el criterio comprometido (1b decide), escribir el veredicto en
  `docs/futures_case.md`.

**Regla dura de cancelación (no una intención):**

> La renovación de Norgate se **cancela el DÍA 3, pase lo que pase**, salvo un **GO limpio
> en el criterio 1b (Δ > +0.15 con IC que no cruza 0)**. La cancelación se **ejecuta ANTES
> de escribir el veredicto**, no después.
>
> RAZÓN: la forma en que un mes se convierte en seis es que el resultado sale
> indeterminado, se le ocurre a uno una variante, y "sólo un mes más". La cancelación va
> primero para que la decisión de renovar sea ACTIVA, no pasiva.

**Recordatorio de protocolo (innegociable):**

> La señal `tsmom` **NO se toca**. Ni lookback, ni sizing, ni umbrales, ni selección de
> instrumentos después de ver resultados. Si el resultado sale flojo y aparece la
> tentación de "probar con lookback de 6 meses sobre el universo nuevo", eso convierte el
> diagnóstico en **caza de variantes** y quema el mes. **Un run, cuatro números, un
> veredicto.**

- **NO** se contrata hasta que este plan esté escrito y revisado. Un mes = una pregunta.
