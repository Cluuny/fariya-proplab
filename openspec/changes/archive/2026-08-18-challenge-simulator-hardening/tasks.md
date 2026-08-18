## 1. Retirar el valor provisional y la perilla oculta

- [x] 1.1 Eliminar `_economic_value` y el cap `s = min(p_survive_cycle, 0.9995)` de `src/challenge.py`
- [x] 1.2 En `simulate_challenge`, dejar de calcular `expected_net`; `leverage_value_curve` queda vacía; `expected_net_value` queda `nan` (o retirar el campo — decidir según consumidores)
- [x] 1.3 Conservar `_funded_phase` y `p_survive_cycle` (los usa `p_burn`, que es correcto)
- [x] 1.4 Revisar `config.FirmRules`: eliminar `profit_split`/`account_capital` si sólo servían al valor retirado; conservar `payout_interval_days`/`n_payouts` (fase fondeada de `p_burn`)

## 2. `expected_days` honesto bajo el guard

- [x] 2.1 `expected_days_to_pass = nan` cuando `insufficient_horizon` es True (hoy sólo nan si `p_cond<=0`)

## 3. Docstrings

- [x] 3.1 Corregir el docstring de cabecera de `challenge.py`: quitar "P(pass) vs leverage curve → optimal multiplier"; reflejar curvas diagnósticas + `optimal_leverage` diferido al objetivo umbral
- [x] 3.2 Documentar en `_funded_phase` la suposición de no-reset del balance tras el payout (los brokers reales SÍ resetean; limitación conocida)

## 4. Reporte

- [x] 4.1 En `report.render_challenge`, dejar de mostrar "Valor por año"; mostrar `P(quemar)` y la curva de P condicional; mantener la bandera de horizonte insuficiente

## 5. Spec

- [x] 5.1 (Sync en archivo) El delta MODIFICA "Métricas económicas" (expected_days nan bajo guard; sin valor provisional) y "Curva de apalancamiento" (sin curva de valor; objetivo UMBRAL sem 9-10; invariante de borde = tarea sem 9-10). Verificar que la implementación cumple al terminar

## 6. Tests

- [x] 6.1 Test: `expected_days_to_pass` es `nan` cuando `insufficient_horizon`
- [x] 6.2 Test: no queda dependencia del cap `0.9995` (la métrica de valor ya no se calcula; `leverage_value_curve` vacía o ausente)
- [x] 6.3 Ajustar/retirar los tests afectados por la retirada del valor provisional (`test_expected_net_value_monotonic_in_edge`, `test_report_integration`); reconvertir el primero a un test de `p_burn`/condicional si aplica
- [x] 6.4 Mantener verdes los tests existentes que NO cambian de comportamiento (contabilidad de tres resultados, `p_burn`↑, guard, fórmula cerrada, invariancia al horizonte)
- [x] 6.5 Toda la suite pasa (`uv run pytest`)

## 7. Cierre

- [x] 7.1 Re-correr el E2E: `optimal_leverage=None`, sin número de valor, `expected_days` nan bajo guard, `P(quemar)` sube con leverage
- [x] 7.2 Commit del fix
