## 1. Configuración de reglas y simulador

- [x] 1.1 Añadir a `src/config.py` una `dataclass FirmRules` (objetivo fase 1, objetivo fase 2, límite de pérdida diaria, drawdown máximo estático, `N` payouts, costo de cuota, payout esperado) con un valor por defecto documentado (sin hardcodear una firma real)
- [x] 1.2 Añadir parámetros del simulador a `config.py`: `block_size` (default > 1, ~20), `n_bootstraps` (~10.000), `horizon_days`, `seed`, y la malla de apalancamiento (rango/paso)

## 2. Motor de remuestreo (block bootstrap)

- [x] 2.1 Implementar el moving-block bootstrap: dado un vector de retornos, `block_size` y un horizonte, generar una matriz `(n_bootstraps, horizon_days)` de trayectorias remuestreadas, vectorizada con numpy y semilla fija
- [x] 2.2 Permitir `block_size=1` (i.i.d.) solo para los tests de validación analítica; el default de producción es > 1
- [x] 2.3 Test: el remuestreo por bloques preserva aproximadamente la volatilidad/estructura de la serie original frente a i.i.d.; determinismo bajo semilla

## 3. Evaluación de barreras (first passage)

- [x] 3.1 Implementar el recorrido de cada trayectoria acumulando equity desde el capital inicial y detectando el primer evento: alcanzar objetivo de fase, violar límite de pérdida diaria, o violar drawdown máximo **estático** (contra capital inicial, no trailing)
- [x] 3.2 Encadenar fase 1 → fase 2 para calcular `P(fase 1)`, `P(fase 2 | fase 1)` y `P(ambas)`; y días esperados hasta pasar
- [x] 3.3 Calcular `P(quemar la cuenta fondeada antes del payout N)` tras pasar ambas fases
- [x] 3.4 Tests: las tres probabilidades en [0,1]; drawdown estático (no trailing) verificado; cambiar reglas cambia el resultado de forma coherente

## 4. Métricas económicas

- [x] 4.1 Implementar el **valor esperado neto de cuotas** (ingreso esperado ponderado por `P(ambas)` y `P(quemar)`, menos costo de cuotas por nº esperado de intentos), con supuestos explícitos
- [x] 4.2 Test de monotonía: una estrategia estrictamente mejor (mayor deriva, misma vol) produce mayor valor esperado neto

## 5. Curva de apalancamiento óptimo

- [x] 5.1 Implementar la curva `P(pasar)` vs multiplicador de apalancamiento (escalar retornos sobre la malla) y localizar el `argmax`
- [x] 5.2 Test: para una estrategia con deriva positiva y `σ>0`, el apalancamiento óptimo es estrictamente menor que el máximo del rango (el óptimo no es el máximo)

## 6. Verificación matemática (oráculo cerrado)

- [x] 6.1 Implementar helper con la fórmula analítica cerrada `P = [1 − e^(−2μb/σ²)] / [1 − e^(−2μ(a+b)/σ²)]`
- [x] 6.2 Test de aceptación (semana 4): retornos sintéticos de deriva cero + barreras simétricas 10/10 → `P(pasar) ≈ 0.5` dentro de tolerancia de Monte Carlo
- [x] 6.3 Test: para deriva y σ conocidas no nulas, la `P(pasar)` simulada coincide con la fórmula cerrada dentro de tolerancia

## 7. API pública e integración

- [x] 7.1 Reemplazar el stub `simulate_challenge` de `src/challenge.py` por la implementación, devolviendo una estructura con todas las salidas (P por fase, días, P(quemar), valor esperado neto, curva de leverage + óptimo)
- [x] 7.2 Integrar (opcional) los resultados del simulador en `src/report.py` para una estrategia dada (p. ej. buy & hold sobre datos limpios)
- [x] 7.3 Verificación E2E: correr el simulador sobre la señal buy & hold del Bloque A y observar salidas coherentes

## 8. Cierre

- [x] 8.1 Confirmar que toda la suite pasa (`uv run pytest`)
- [x] 8.2 Commit del hito de semanas 4-5 (simulador verificado + curva de apalancamiento óptimo)
