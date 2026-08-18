# backtest-engine Specification

## Purpose

El motor de backtest traduce pesos objetivo en retornos netos aplicando los costos reales de operar (comisión, spread, slippage, impacto). Es el único componente que aplica costos, y su fidelidad es lo que separa una estrategia rentable de un espejismo.

## Requirements

### Requirement: Anualización consistente con el calendario observado

El sistema SHALL anualizar el Sharpe (y cualquier métrica anualizada) usando el número de barras por año **observado** en la serie, no una constante global fija. Series con distinto calendario (FX ~260/año, índices ~247/año tras descartar fines de semana) SHALL anualizarse cada una con su propio conteo, para no introducir un sesgo sistemático.

#### Scenario: El Sharpe se anualiza con las barras/año de la serie
- **WHEN** se calcula el Sharpe de dos series con distinto número de barras por año
- **THEN** cada una se anualiza con su propio conteo observado de barras por año, no con un factor común fijo

### Requirement: Cálculo de retornos netos con costos

El sistema SHALL recibir un DataFrame de pesos objetivo y una serie de precios, y devolver una serie de retornos netos que incorpore comisión, spread, slippage, impacto y **swap** (cargo de mantener posición). El motor SHALL ser el único módulo del sistema que aplica costos de operación. El swap SHALL aplicarse como un cargo **diario proporcional a `|peso|`** de la posición mantenida (no al turnover), de modo que una estrategia de holding largo (que rota poco pero mantiene semanas) incurra el costo real de mantener.

**LIMITACIÓN CONOCIDA — el swap no tiene dirección (bloqueante de H002):** el swap se modela como un cargo siempre positivo sobre `|peso|`, sin distinguir el lado (largo/corto) ni el signo del diferencial de tasas. Para estrategias de trend (H001) es una aproximación conservadora aceptable (siempre resta; errar hacia abajo es el lado seguro). Para una estrategia de **carry (H002)** el swap ES el retorno de la estrategia (largo AUDUSD históricamente cobraba, corto pagaba); con este modelo H002 sería estructuralmente incapaz de ganar y su falsador la mataría sin haberla probado. Darle dirección al swap (diferencial de tasas con signo) es un **prerrequisito de H002**, no está implementado.

#### Scenario: Los costos reducen el retorno
- **WHEN** se corre el motor con costos positivos sobre una estrategia que rota posiciones
- **THEN** el retorno neto acumulado es estrictamente menor que el retorno bruto de la misma estrategia sin costos

#### Scenario: Sin rotación, sólo costo de mantener
- **WHEN** se corre el motor sobre una estrategia buy & hold que no rota posiciones tras la entrada inicial
- **THEN** los costos de **transacción** (turnover) posteriores a la entrada son cero, pero el **swap** se acumula cada día que se mantiene la posición, proporcional a `|peso|`

#### Scenario: El swap escala con los días mantenidos
- **WHEN** se comparan dos posiciones idénticas mantenidas por distinto número de días
- **THEN** el costo de swap total es mayor para la que se mantiene más días (proporcional a los días × `|peso|`)

### Requirement: Estimación de volatilidad segura ante huecos

El sistema SHALL proveer una estimación de volatilidad por instrumento que se calcule sobre los **días de cotización propios** de cada instrumento, excluyendo los retornos cero que el forward-fill inyecta en los huecos de calendario. En un DataFrame combinado, un índice tiene retorno cero cada día que un par de FX cotizó pero él no; incluir esos ceros **deflacta** su vol estimada (~20%) y sobredimensionaría los índices en un sizing por volatilidad inversa. El sizing por vol inversa SHALL usar esta estimación, no la volatilidad de la serie de retornos con ceros de relleno.

Nota: el forward-fill también extendería el último precio si una serie termina antes que las otras (cola). Hoy no aplica (todas las series cierran en la misma fecha), pero es una limitación conocida al añadir un instrumento de historia más corta.

#### Scenario: La vol de un índice con huecos no se deflacta
- **WHEN** se estima la volatilidad de un índice que no cotiza en una fracción de los días del DataFrame combinado
- **THEN** la estimación se aproxima a la vol calculada sobre los días de cotización propios del índice, no a la vol deflactada por los ceros de relleno

### Requirement: Reproducción de un Sharpe histórico conocido

El sistema SHALL verificar el motor contra un Sharpe de referencia de un índice, **nombrando con precisión qué es externo y qué es interno**. La verificación EXTERNA SHALL ser que la serie de precios ES el índice: sus endpoints (al menos el inicial, idealmente también el final) coinciden con los cierres públicos del índice. Si la serie es el índice, su Sharpe es el del índice **por construcción** — esto NO es una comparación contra una cifra publicada ni un paper. El acuerdo entre el Sharpe geométrico (CAGR/vol) y el de `engine.sharpe` (media aritmética) sobre la misma serie es un cross-check **interno** entre estimadores, no una verificación externa. El motor SHALL reproducir el Sharpe de referencia dentro de la tolerancia acordada.

#### Scenario: Buy & hold reproduce el Sharpe del índice
- **WHEN** se corre el motor con la señal buy & hold sobre la serie histórica de un índice cuyos endpoints coinciden con los cierres públicos del índice
- **THEN** el Sharpe calculado por el motor coincide con el de referencia dentro de la tolerancia, y la procedencia distingue la verificación externa (la serie es el índice) del cross-check interno (geométrico vs aritmético)

### Requirement: Pureza y determinismo del motor

El sistema SHALL calcular retornos de forma determinista: dadas las mismas entradas (pesos, precios y parámetros de costo), el motor produce siempre los mismos retornos, sin depender de estado externo.

#### Scenario: Resultado determinista
- **WHEN** se corre el motor dos veces con idénticos pesos, precios y parámetros de costo
- **THEN** ambas ejecuciones producen series de retornos idénticas

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
