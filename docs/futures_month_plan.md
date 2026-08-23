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
- El único output es de medición: los tres números de abajo.

## Los tres números, EN ORDEN (2.3)

1. **Bruto de exceso de trend** con **IC 95% por block bootstrap** (bloques ~21 días para
   respetar autocorrelación de holding mensual). *Nota:* nuestro bruto ya es de exceso (P&L
   de precio, sin interés sobre colateral) — comparable directo al 0.42 y al 0.32 de la
   industria (ver `docs/futures_case.md`, corrección de comparabilidad).
2. **N_eff** con continuos **reales** (no proxies ETF) — autovalores de la matriz de
   correlación del universo operable. Re-verifica el criterio (2) con datos reales (los
   ETFs inflaban).
3. **Coste de roll MEDIDO** por mercado (del calendar spread real de los continuos), para
   sustituir la estimación de 0.19%/año del Bloque 1 por un número observado.

El número (1) es el que decide. (2) y (3) son verificaciones de soporte.

## Criterio de decisión — COMPROMETIDO (2.4)

Sobre el número (1), bruto de exceso de trend con su IC 95%:

| resultado | decisión |
|---|---|
| bruto **> 0.42** y el IC **NO cruza** 0.42 | **GO** — el vehículo + un edge que supera el listón. Opción A viva con evidencia real. |
| bruto **< 0.42** y el IC **NO cruza** 0.42 | **Opción A CERRADA POR EVIDENCIA** — ni el universo real de futuros da el bruto necesario. Se cierra el programa de trend/futuros, no por falta de dinero. |
| el IC **cruza** 0.42 | **INDETERMINADO** — y entonces, honestamente: **los futuros resuelven el COSTE, no el EDGE.** No se puede afirmar que la migración añade edge. Se documenta como no-concluyente y NO se compromete más capital sobre esa base. |

## Expectativa — COMPROMETIDA antes de correr (2.5)

Predicción honesta: bruto de exceso **0.30–0.45**, con el **IC cruzando 0.42**. Es decir,
el resultado **más probable es INDETERMINADO**. Base: H007-A dio 0.370 (0.22 SE del
listón) y la industria da ~0.32 bruto de comisiones — ambos justo por debajo o al borde de
0.42. Sería sorprendente (y bienvenido) un GO limpio; sería informativo un cierre limpio.
Lo esperado es la zona de ruido. Comprometer esto por adelantado evita leer un
indeterminado como un GO.

## Plan de ejecución (2.6)

- **Día 0 (contratar):** suscribir Norgate Futures (~$50, ~1/10 de un challenge). Bajar los
  continuos ajustados por roll (EOD) de los ~25–30 mercados listados.
- **Día 1:** cargar a `data/futures/`, correr `engine.backtest` con `signals.tsmom` sin
  modificar sobre el universo completo. Calcular los tres números (bruto+IC, N_eff, roll
  medido). Un script de diagnóstico dedicado (`scripts/futures_diagnostic.py`), sin
  pre-registro.
- **Día 2–3:** aplicar el criterio comprometido, escribir el veredicto en
  `docs/futures_case.md`. **Deadline de cancelación:** cancelar la renovación de Norgate
  ANTES del fin del primer ciclo de facturación (típicamente 30 días). El diagnóstico cabe
  en 2–3 días; no hay razón para un segundo mes salvo que el resultado sea GO y se decida
  operar de verdad.
- **NO** se contrata hasta que este plan esté escrito y revisado. Un mes = una pregunta.
