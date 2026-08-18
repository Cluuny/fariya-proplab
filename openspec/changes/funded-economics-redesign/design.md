## Context

Ver `proposal.md` — Why. El change `three-outcome-accounting` corrigió la *contabilidad* (PASÓ/FALLÓ/SIN ABSORBER visibles y correctos), pero la *economía* siguió plegando SIN ABSORBER en fallo vía `p_both`. El review lo demostró con una estrategia de Sharpe 0.8: `optimal_leverage` cae en el borde del grid (`3.0×`), lo contrario de la tesis. El código relevante está en `src/challenge.py`: `_first_passage` (registro de días), `simulate_challenge` (p_both, p_burn, expected_days), `_expected_net_value` (attempts, daily_capital_cost), y la curva de leverage.

## Goals / Non-Goals

**Goals:**
- Métricas de decisión condicionadas a absorción; ninguna pliega SIN ABSORBER en fallo.
- `p_burn` correcto (sube con el apalancamiento); `expected_days` incluye intentos fallidos.
- Objetivo = valor por unidad de tiempo; `payout` derivado de la fase fondeada; sin `daily_capital_cost`.
- Guard de horizonte insuficiente; sin centinela mágico.
- Invariante de spec anti-pliegue + tests que lo protegen (incl. óptimo no en el borde).

**Non-Goals:**
- Universo (Nikkei/Brent) + mapeo Dukascopy, swap en `CostModel`, `sum(|w|)≤1`, límite diario sobre cierres, pre-registro H001 — van en `universe-and-costs`/H001.
- Cambiar el bootstrap por bloques o la verificación analítica (se mantienen).

## Decisions

### D1 — Probabilidad de decisión condicional a absorción
`p_cond = p_pass / (p_pass + p_fail)` por fase. Es la probabilidad de primer paso correcta del problema de doble barrera (en tiempo infinito la absorción es casi segura, y `p_cond` es su límite). `expected_attempts = 1/(p_cond1·p_cond2)`. La curva diagnóstica de P(pasar) también usa la condicional. **Alternativa:** seguir con `p_both` crudo — es el bug: cuenta sin-absorber como no-paso e infla los intentos a bajo apalancamiento.

### D2 — Guard de horizonte insuficiente
Si `p_unresolved > τ` (τ≈0.05) en alguna fase, la estimación condicional es poco fiable (pocas trayectorias absorbieron). El sistema marca `insufficient_horizon` y devuelve `expected_net_value = nan` (no un número). El campo/bandera viaja en `ChallengeResult`. **Por qué:** a Sharpe 0.8 y bajo apalancamiento, absorber pide ~5040 días; 756 no alcanza. Reportar un número ahí es engañoso. **Alternativa:** extender el horizonte a 20 años siempre — caro y no resuelve el caso patológico; mejor marcar la bandera.

### D3 — `p_burn` como complemento de FALLA (bug 2)
Sobrevivir un ciclo de payout = no tocar la barrera de pérdida. En términos de la fase usada como proxy de ciclo, `p_survive_cycle = p_fail_condicional_complemento` (no `p_phase2`). `p_burn_before_payout = 1 - p_survive_cycle**N`. Verificación de signo: `P(quemar)` debe **subir** con el apalancamiento. **Nota:** conviene modelar el ciclo de payout como su propia barrera (sólo la de pérdida, sin objetivo), ver D5.

### D4 — `expected_days` con intentos fallidos (bug 3)
`_first_passage` registra el día de absorción para PASADAS **y** QUEMADAS (hoy sólo pasadas; las quemadas quedan en `horizon`). El tiempo esperado por intento = media del día de absorción sobre las trayectorias que absorbieron (pasan o queman). El tiempo total hasta pasar ≈ `expected_attempts × tiempo_por_intento` (aproximación; los intentos fallidos previos consumen su propio tiempo de absorción). **Alternativa:** sólo ganadoras — subestima el tiempo, justo lo que el objetivo económico intenta poner en precio.

### D4b — DECISIÓN (sem 6): `optimal_leverage = None`, objetivo diferido
Tras implementar D1–D5, el óptimo por valor/tiempo cae en el borde del grid (máximo). No es artefacto de truncación (todo eso está arreglado): es una propiedad real de una apuesta con **dinero de la casa** bajo valor esperado riesgo-neutral. El documento maestro se contradice — §2.1 (minimizar volatilidad → mínimo) vs §3.4 ("valor esperado neto decide" → para dinero de la casa, máximo). Un óptimo interior sólo emerge de un objetivo que penalice la varianza intrínsecamente, y elegirlo hoy lo fijaría una perilla de modelado, no los datos. **Decisión:** `optimal_leverage = None` con motivo explícito; reportar ambas curvas; construir el objetivo real (valor/tiempo con payout endógeno) en sem 9-10 con el modelo de fase fondeada que el portafolio exigirá. Alternativas rechazadas: `argmax P` (mínimo degenerado), `min k factible` (`horizon_days`/`leverage_min` son perillas ocultas), growth-optimal (ignora la barrera absorbente del drawdown, sobre-apalanca). **Invariante para el objetivo futuro:** óptimo en el borde del grid = objetivo mal especificado → error. **Desbloqueo:** el veredicto de H001 (sem 8) usa Sharpe, invariante al apalancamiento, así que no depende de esta decisión.

### D5 — Matar `daily_capital_cost`; derivar `payout` de la fase fondeada; objetivo valor/tiempo (provisional)
Se elimina `daily_capital_cost` de `config` (parámetro inventado que fijaba la ubicación del óptimo). El `payout` esperado por ciclo se **deriva simulando la fase fondeada**: partiendo de la cuenta fondeada, simular con block bootstrap hasta el siguiente payout o quema; `payout_esperado = profit_split × E[retorno acumulado | sobrevive hasta el payout]`. Esto hace que el payout **escale con el retorno** (sube con la vol/apalancamiento), mientras `P(quemar)` sube más rápido. El objetivo de decisión = **valor por unidad de tiempo** = `(ingreso esperado de payouts − costo esperado de cuotas) / tiempo total esperado`. El óptimo interior emerge del tira y afloja real, sin parámetros inventados. **Riesgo/decisión abierta:** el `profit_split` (p. ej. 80/20) y el intervalo de payout son reglas de firma reales → van en `FirmRules` como parámetros de firma (no inventados), no como un costo ad hoc. **Alternativa:** payout fijo — es parte del bug (bajar leverage no cuesta ingresos, sólo sube P).

### D6 — Sin centinela mágico
`_expected_net_value` devuelve `nan` cuando no hay valor definido (p_both≤0 o guard de horizonte), no `-1e12`. La curva de leverage excluye `nan` del `argmax` (`np.nanargmax` sobre valores finitos; si todos son `nan`, `optimal_leverage` es indefinido/`nan`). **Por qué:** `-1e12` domina cualquier comparación y ensucia el óptimo.

### D7 — Tests que protegen el invariante
- **Regresión de borde:** para una estrategia con edge, `optimal_leverage` NO puede ser `leverage_min` ni `leverage_max` (la firma de un objetivo mal especificado).
- **Property de invariancia al horizonte:** `p_cond` de decisión ~ estable ante dos horizontes; `p_both` crudo cambia.
- **Signo de `p_burn`:** sube con el apalancamiento.
- **Guard:** con horizonte corto y estrategia lenta, `insufficient_horizon` marcado y `expected_net_value` es `nan`.
- Se mantiene el test contra la fórmula cerrada (deriva cero → P≈0.5) y los de contabilidad de tres resultados.

## Risks / Trade-offs

- **Derivar el payout añade una sub-simulación (fase fondeada)** → más costo computacional y una pieza de modelado nueva. Mitigación: reusar `block_bootstrap`/`_first_passage` con sólo la barrera de pérdida; exponer `n_bootstraps` para tests.
- **La aproximación `tiempo_total ≈ intentos × tiempo_por_intento`** ignora correlaciones entre número de intentos y su duración → aceptable a primer orden; documentar el supuesto.
- **`nan` propagándose** puede romper consumidores (report) → manejar explícitamente en `report.render_challenge` (mostrar "horizonte insuficiente").
- **El óptimo podría seguir en el mínimo** para estrategias con edge fuerte y payout que no escala lo suficiente → si ocurre tras el payout derivado, es un resultado válido (operar a mínima vol), pero el test de borde distingue "válido" de "artefacto" exigiendo que no sea consecuencia de truncación/payout fijo/centinela.

## Open Questions

- Valor del umbral del guard `τ` (¿5%, 2%?): diferible; default 5% documentado.
- `profit_split` e intervalo de payout concretos: son reglas de firma; se parametrizan en `FirmRules` con un default documentado y se calibran con una firma real más adelante (no bloquea el diseño).
- Definición exacta de "ciclo de payout" para `p_burn` (¿ventana fija de días hasta el payout, o hasta acumular el objetivo de payout?): se fija en implementación con un supuesto explícito; el contrato del spec es sólo que `p_burn` suba con el apalancamiento y no cuente sin-absorber como quema.
