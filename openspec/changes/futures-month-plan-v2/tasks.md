# Tareas

## 1. (A) Documentar que el test de nivel no discrimina
- [x] 1.1 Mostrar la aritmética del IC (0.370 ± 1.96×0.240 = [−0.10, +0.84]) y que no
  cruzar 0.42 exigiría bruto ~0.85+ o ~0.0.
- [x] 1.2 Concluir: INDETERMINADO ~seguro por construcción; el nivel no justifica el gasto solo.

## 2. (B) Añadir el número 1b — Δ vs nuestro propio CFD
- [x] 2.1 Definir Δ = bruto(futuros) − bruto(CFD, mismo período), SE(Δ) ≈ 0.17 por
  correlación ~0.75, bootstrap PAREADO por bloques sobre ventana común EXACTA.
- [x] 2.2 Criterio comprometido: Δ > +0.15 → aportan; Δ ≈ 0 → opción A muerta por evidencia
  propia; IC cruza 0 → no concluyente.
- [x] 2.3 Expectativa comprometida: Δ +0.05 a +0.20, IC probablemente cruza 0 pero más estrecho.
- [x] 2.4 Reordenar (2.3): 1b primero (decide), luego 1 (nivel), 2 (N_eff), 3 (roll).
- [x] 2.5 Actualizar (2.4) y (2.5) para que 1b sea el criterio/expectativa que decide.

## 3. (C) Endurecer el deadline
- [x] 3.1 Regla dura: cancelar el DÍA 3 pase lo que pase, salvo GO limpio en 1b; ejecutar
  la cancelación ANTES de escribir el veredicto.

## 4. (D) Recordatorio de protocolo
- [x] 4.1 `tsmom` no se toca (lookback/sizing/umbrales/selección post-hoc); un run, cuatro
  números, un veredicto.

## 5. Consistencia
- [x] 5.1 Actualizar referencias "tres números" → "cuatro números" en el resto del plan.
