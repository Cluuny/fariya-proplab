## MODIFIED Requirements

### Requirement: Ausencia de look-ahead (convención de shift)

El sistema SHALL calcular retornos sin mirar el futuro: el peso decidido en el día `t-1` captura el retorno del día `t` (`w_{t-1} · ret_t`). El cálculo SHALL ser **seguro ante huecos de calendario**: cuando se combinan instrumentos con calendarios distintos (el DataFrame tiene NaN donde un instrumento no cotizó), el retorno que cruza un hueco SHALL atribuirse al **día de reapertura** —ni dropearse (un `pct_change().fillna(0)` ingenuo pone en 0 tanto el día del hueco como el de reapertura, perdiendo el retorno real) ni adelantarse al día equivocado (look-ahead sutil)—; y un día no cotizado SHALL rendir 0 (una posición mantenida se mantiene, sin movimiento). Esta convención SHALL ser verificable de extremo a extremo con una prueba de sesgo (señal que mira el futuro → Sharpe absurdo; señal que mira el pasado → Sharpe modesto), **sobre datos con calendarios desalineados**.

#### Scenario: Una señal que mira el futuro da Sharpe absurdo
- **WHEN** se corre el motor con una señal cuyo peso es el signo del retorno del día siguiente (mira el futuro), sobre instrumentos con calendarios desalineados
- **THEN** el Sharpe resultante es absurdamente alto (p. ej. > 5); si no lo es, la convención de `shift` está rota en la dirección que oculta el bug

#### Scenario: Una señal que sólo mira el pasado da Sharpe modesto
- **WHEN** se corre el motor con una señal cuyo peso es el signo del retorno del día anterior (sólo mira el pasado), sobre instrumentos con calendarios desalineados
- **THEN** el Sharpe resultante es modesto (p. ej. < 2); si es enorme, hay look-ahead

#### Scenario: El retorno que cruza un hueco de calendario no se pierde ni se adelanta
- **WHEN** un instrumento no cotiza en un día que otros del universo sí (hueco de calendario en el DataFrame combinado)
- **THEN** el día del hueco rinde 0 y el retorno que cruza el hueco se atribuye al día de reapertura, sin dropearse ni adelantarse a un día anterior
