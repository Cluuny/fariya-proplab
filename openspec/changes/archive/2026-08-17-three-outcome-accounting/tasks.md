## 1. Contabilidad de tres resultados en el motor

- [x] 1.1 Reescribir `_first_passage` para devolver un estado de tres valores por trayectoria (PASÓ / FALLÓ / SIN ABSORBER) más los días de paso; las trayectorias aún activas al terminar el horizonte son SIN ABSORBER (D1)
- [x] 1.2 En `simulate_challenge`, calcular `P(pasar)`, `P(fallar)` y `P(sin_absorber)` por fase; verificar que suman 1 por construcción
- [x] 1.3 Añadir a `ChallengeResult` los campos `p_fail`, `p_unresolved` y `horizon_days`, conservando los campos existentes con semántica de "PASAR" ya limpia de truncación (D2)

## 2. Horizonte honesto

- [x] 2.1 Subir `SimulatorParams.horizon_days` por defecto a ~756 días (~3 años) con comentario que explique por qué (FTMO sin límite de tiempo) (D3)
- [x] 2.2 Asegurar que la curva de leverage usa el mismo horizonte largo (hoy reusa `params`, confirmar tras el cambio)

## 3. Optimizador de leverage sobre valor económico

- [x] 3.1 Incorporar el costo del tiempo/capital inmovilizado en `_expected_net_value` para que dependa de los días esperados hasta pasar, con supuestos explícitos (D5); añadir parámetro(s) necesarios a `config`
- [x] 3.2 Cambiar `optimal_leverage` para que maximice `expected_net_value(k)` sobre la malla, no `argmax(p_both)`; seguir reportando la curva `P(pasar)` como diagnóstico (D4)
- [x] 3.3 Recalcular `expected_attempts`, `expected_net_value` y `p_burn_before_payout` sobre la contabilidad corregida (sin truncación inflando/deprimiendo)

## 4. Reporte y documentación

- [x] 4.1 Mostrar `P(sin absorber)` y el horizonte en `report.render_challenge`; aclarar que la curva `P` es diagnóstica y la decisión sale del valor económico
- [x] 4.2 Añadir comentario en `config.py`: P&L aditivo correcto para sizing estático; el espacio-log vuelve solo con sizing compuesto + trailing (D6)

## 5. Spec

- [x] 5.1 (Sync en archivo) El delta ya AÑADE "Contabilidad de tres resultados" y MODIFICA "Curva de probabilidad frente a apalancamiento"; verificar que la implementación cumple ambos al terminar

## 6. Tests

- [x] 6.1 Regresión anti-plegado: con retornos de baja deriva y horizonte corto, `P(pasar)+P(fallar)+P(sin_absorber)==1` y `P(sin_absorber) > 0` claramente; el test FALLA si sin-absorber se pliega en fallo
- [x] 6.2 Monotonía: con horizonte largo y deriva positiva, `P(pasar)` es mayor a menor apalancamiento (menos leverage → más P)
- [x] 6.3 Óptimo de decisión interior: `optimal_leverage` (sobre `expected_net_value`) es estrictamente menor que el máximo del rango y no es el mínimo
- [x] 6.4 Mantener el test de verificación contra la fórmula cerrada (deriva cero → `P≈0.5`) y ajustar cualquier test existente afectado por los nuevos campos/semántica
- [x] 6.5 Actualizar `test_challenge.py::test_optimal_leverage_is_interior` a la nueva semántica (decisión sobre valor económico)

## 7. Cierre

- [x] 7.1 Confirmar que toda la suite pasa (`uv run pytest`)
- [x] 7.2 Re-correr el E2E de leverage y verificar la nueva forma (curva `P` monótona; óptimo de decisión interior)
- [x] 7.3 Commit del fix
