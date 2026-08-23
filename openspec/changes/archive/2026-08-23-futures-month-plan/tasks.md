# Tareas

## 1. Reencuadre del número decisivo
- [x] 1.1 Documentar por qué el plan anterior (re-verificar N_eff) apunta al criterio
  equivocado: el número que decide es el bruto de trend sobre el universo real, no la amplitud.
- [x] 1.2 Establecer el listón (0.424) y la brecha actual (H007-A 0.370 = 0.22 SE, indistinguible).

## 2. Especificación del diagnóstico
- [x] 2.1 Listar el universo (~25–30 mercados: rates ZT/ZF/ZN, índices ES/NQ/YM/RTY,
  FX 6E/6J/6B/6A/6C, energía CL/RB/HO, metales GC/SI/HG; agrícolas y NG excluidos por roll).
- [x] 2.2 Fijar que la señal `signals.tsmom` va SIN modificar (mismo lookback/sizing).
- [x] 2.3 Declarar naturaleza: diagnóstico, sin pre-registro, sin consumir cola, sin holdout.

## 3. Los tres números y el criterio
- [x] 3.1 Definir los tres outputs en orden: bruto de exceso + IC 95% block-bootstrap,
  N_eff con continuos reales, coste de roll medido.
- [x] 3.2 Escribir el criterio de decisión comprometido (GO / CERRADA / INDETERMINADO).
- [x] 3.3 Escribir la expectativa comprometida (0.30–0.45, IC cruza → INDETERMINADO probable).

## 4. Ejecución
- [x] 4.1 Plan de ejecución: descargas día 0, run día 1, veredicto día 2–3, deadline de cancelación.
- [x] 4.2 Dejar explícito: NO contratar hasta que el plan esté escrito y revisado.
