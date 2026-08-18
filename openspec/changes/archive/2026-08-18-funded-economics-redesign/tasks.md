## 1. Registro de absorción para ambos resultados (bug 3, base)

- [x] 1.1 En `_first_passage`, registrar el día de absorción para PASADAS y QUEMADAS (antes sólo pasadas); devolver `day_absorbed`
- [x] 1.2 Test: las trayectorias quemadas tienen día de absorción; las sin absorber quedan aparte (cubierto por el guard/invariancia)

## 2. Probabilidad condicional a absorción (bug 1)

- [x] 2.1 `p_cond = p_pass/(p_pass+p_fail)` por fase; `expected_attempts = 1/(p_cond1·p_cond2)` (nunca `1/p_both`)
- [x] 2.2 La curva diagnóstica de P(pasar) vs leverage usa la condicional (monótona), no `p_both`
- [x] 2.3 Exponer `p_pass_conditional` en `ChallengeResult`, sin romper la contabilidad de tres resultados

## 3. Guard de horizonte insuficiente

- [x] 3.1 Si `p_unresolved > τ` (default 5%) en alguna fase: `insufficient_horizon=True` y `expected_net_value = nan`
- [x] 3.2 Test: con horizonte corto y estrategia lenta, el guard se activa y no reporta valor numérico

## 4. p_burn correcto (bug 2)

- [x] 4.1 Fase fondeada con sólo la barrera de pérdida; `p_survive_cycle` = fracción que sobrevive; `p_burn = 1 - p_survive**N`
- [x] 4.2 Test de signo: `p_burn` crece con el apalancamiento

## 5. Objetivo económico — parcial (DECISIÓN: diferir el óptimo)

- [x] 5.1 Eliminar `daily_capital_cost` de `FirmRules`/`config`
- [x] 5.2 Derivar `payout` simulando la fase fondeada (escala con el retorno); `profit_split`/`payout_interval_days`/`account_capital` en `FirmRules`
- [x] 5.3 Valor por unidad de tiempo (renewal: payouts hasta quemar) usando `expected_days` que incluye intentos fallidos — **provisional**
- [x] 5.4 **DECISIÓN (sem 6):** `optimal_leverage = None` con motivo explícito; NO derivar un óptimo de ninguna curva todavía. El objetivo real (valor/tiempo con payout endógeno) se construye en sem 9-10 con el modelo de fase fondeada del portafolio. Rechazadas: `argmax P` (mínimo degenerado), `min k factible` (perillas ocultas), growth-optimal (ignora barrera absorbente)

## 6. Sin centinela mágico

- [x] 6.1 `_economic_value` devuelve `nan` (no `-1e12`) cuando el valor es indefinido

## 7. Reporte

- [x] 7.1 `report.render_challenge`: muestra P condicional, `P(quemar)`, valor/año provisional, bandera de horizonte insuficiente, ambas curvas, y `optimal_leverage = "no definido — <motivo>"`

## 8. Spec

- [x] 8.1 Delta: AÑADE "Ninguna métrica pliega sin-absorber en fallo"; MODIFICA "Métricas económicas" y "Curva de apalancamiento" con la DECISIÓN (optimal=None), el objetivo comprometido (sem 9-10) y el INVARIANTE de borde

## 9. Tests que protegen el invariante

- [x] 9.1 `optimal_leverage is None` con motivo, y ambas curvas presentes (reemplaza la regresión de borde: no hay óptimo que pueda caer en el borde todavía; el invariante de borde queda en el spec para el objetivo futuro)
- [x] 9.2 Property de invariancia al horizonte: `p_pass_conditional` ~estable entre dos horizontes, mientras `p_both` crudo cambia (con sin-absorber alto al horizonte corto)
- [x] 9.3 Mantener el test contra la fórmula cerrada (deriva cero → P≈0.5) y los de contabilidad de tres resultados
- [x] 9.4 Toda la suite pasa (`uv run pytest`) — 46 tests

## 10. Cierre

- [x] 10.1 Re-correr el E2E con una estrategia con edge (Sharpe ~0.8) y verificar: `P(quemar)` sube con leverage, curva P condicional monótona, `optimal_leverage=None`, guard cuando el horizonte no alcanza
- [x] 10.2 Commit del fix
