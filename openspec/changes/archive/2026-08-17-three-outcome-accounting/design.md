## Context

Ver `proposal.md` — Why. El bug está confirmado a nivel de código en `src/challenge.py`: `_first_passage` inicia `passed=False` y solo lo vuelve `True` al tocar el objetivo; las trayectorias que llegan al horizonte sin absorber quedan en `False` y se promedian como fracaso en `p_phase1 = passed.mean()`. La curva de leverage (`simulate_challenge` con `with_leverage_curve=True`) reusa `params.horizon_days` (252 por defecto), así que el sesgo golpea el extremo de bajo apalancamiento.

## Goals / Non-Goals

**Goals:**
- Separar PASÓ / FALLÓ / SIN ABSORBER; nunca plegar sin-absorber en fallo.
- Horizonte honesto (largo) por defecto y reportado.
- Optimizador de leverage sobre valor esperado neto, no sobre `argmax P`.
- Métricas económicas coherentes con la contabilidad corregida.
- Tests de regresión que fallen si el bug reaparece.

**Non-Goals:**
- Datos reales de Dukascopy (bloque aparte, depende del usuario).
- Pre-registro H001 (otro change).
- Cambiar el modelo de P&L aditivo (es correcto; solo se documenta el caso trailing/compuesto).

## Decisions

### D1 — `_first_passage` devuelve un estado de tres valores por trayectoria
Se reemplaza `(passed, day_passed)` por un vector de estado `outcome ∈ {PASS, FAIL, UNRESOLVED}` (más `day_passed` para las que pasan). Al terminar el bucle, las trayectorias que siguen `active` (ni pasaron ni quemaron) son `UNRESOLVED`. `P(pasar)=mean(outcome==PASS)`, `P(fallar)=mean(==FAIL)`, `P(sin_absorber)=mean(==UNRESOLVED)`; suman 1 por construcción. **Alternativa:** mantener dos booleanos `passed`/`burned` e inferir el tercero — equivalente, pero un enum explícito es menos propenso a que un futuro cambio vuelva a plegar estados.

### D2 — `ChallengeResult` gana campos, sin romper los existentes
Se añaden `p_fail`, `p_unresolved` y `horizon_days` (por fase o agregados). Los campos actuales (`p_phase1`, `p_phase2`, `p_both`, etc.) se conservan con su semántica de "probabilidad de PASAR", ahora limpia de truncación. `report.render_challenge` muestra además `P(sin absorber)`.

### D3 — Horizonte largo por defecto (~756 días ≈ 3 años)
FTMO eliminó el límite de tiempo, así que el horizonte del simulador es una elección de modelado, no una regla de la firma. Se sube `SimulatorParams.horizon_days` a ~756 para que `P(sin_absorber)` sea pequeño en régimen normal; de todos modos se reporta para que la truncación residual sea auditable, no invisible. **Alternativa:** horizonte infinito (correr hasta absorber) — descartada: puede no terminar para deriva ~0; el horizonte acotado + reporte explícito de sin-absorber es honesto y termina siempre.

### D4 — El apalancamiento de decisión maximiza `expected_net_value`, no `P`
Matemática: al escalar retornos por `k`, el ratio de deriva del problema de doble barrera es `2μa/(kσ²)`, que crece cuando `k→0`, luego `P(pasar)→1`. La curva `P` es monótona decreciente en `k`; su `argmax` es el `k` mínimo, que como decisión implicaría esperar casi infinito. El óptimo interior legítimo aparece solo al poner precio al tiempo: `expected_net_value` penaliza los días esperados (capital inmovilizado) y el eventual rendirse. Por eso `optimal_leverage = argmax_k expected_net_value(k)`. La curva `P(pasar)` se sigue reportando como diagnóstico. **Alternativa:** seguir con `argmax P` — es el bug; produciría siempre el leverage mínimo tras el fix.

### D5 — `expected_net_value` debe reflejar el costo del tiempo
Para que D4 dé un óptimo interior, `expected_net_value` SHALL depender de los días esperados hasta pasar (no solo de `p_both`). Se incorpora un costo por tiempo/capital inmovilizado (parámetro en `config`, p. ej. costo de oportunidad diario o un tope de días tras el cual se asume rendirse). Con `k` muy bajo, los días esperados explotan → el valor cae; con `k` muy alto, `P` cae → el valor cae; el óptimo queda en medio. **Nota:** el diseño exacto de este término es la decisión económica clave del change y se fija en implementación con supuestos explícitos y un test de forma (óptimo interior).

### D6 — Comentario de P&L aditivo en `config.py`
Se documenta que aditivo es correcto para sizing estático contra capital inicial, y que solo con sizing compuesto sobre cuenta fondeada + regla trailing volvería a importar el espacio-log. Es documentación, no cambio de comportamiento.

## Risks / Trade-offs

- **Costo computacional del horizonte largo** (~3× iteraciones en `_first_passage`) → Mitigación: el bucle sigue vectorizado sobre trayectorias; exponer `n_bootstraps`/`horizon_days` para bajarlos en tests; `break` temprano cuando no quedan trayectorias activas ya existe.
- **El término de costo de tiempo en `expected_net_value` es un supuesto económico** → Mitigación: encapsularlo con supuestos explícitos y cubrir con un test de forma (óptimo interior) y de monotonía, no con un número mágico.
- **Cambio de forma de la curva puede sorprender** (antes pico a 1.5×, ahora monótona) → Mitigación: el reporte deja claro que la curva `P` es diagnóstica y que la decisión sale del valor económico; se documenta en el change.
- **Compatibilidad de `ChallengeResult`** → Mitigación: solo se AÑADEN campos; el E2E y `report` siguen funcionando.

## Open Questions

- Valor exacto de `horizon_days` (¿756, 1000, 1260?): diferible; se fija con un default documentado y se puede barrer. No cambia el contrato ni las tareas.
- Forma precisa del término de costo de tiempo en `expected_net_value` (costo de oportunidad diario vs. tope de días con rendición): se decide en implementación bajo D5; cualquiera de las dos satisface el contrato (óptimo interior + penaliza el tiempo).
