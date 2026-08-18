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

### Requirement: Reproducción de un Sharpe histórico conocido

El sistema SHALL, mediante una estrategia buy & hold sobre un índice, reproducir el Sharpe histórico conocido de ese índice dentro de una tolerancia acordada. Si no lo reproduce, el motor se considera incorrecto y no verificado.

#### Scenario: Buy & hold reproduce el Sharpe del índice
- **WHEN** se corre el motor con la señal buy & hold sobre la serie histórica de un índice cuyo Sharpe histórico es conocido
- **THEN** el Sharpe calculado por el motor coincide con el histórico conocido dentro de la tolerancia definida

### Requirement: Pureza y determinismo del motor

El sistema SHALL calcular retornos de forma determinista: dadas las mismas entradas (pesos, precios y parámetros de costo), el motor produce siempre los mismos retornos, sin depender de estado externo.

#### Scenario: Resultado determinista
- **WHEN** se corre el motor dos veces con idénticos pesos, precios y parámetros de costo
- **THEN** ambas ejecuciones producen series de retornos idénticas

### Requirement: Ausencia de look-ahead (convención de shift)

El sistema SHALL calcular retornos sin mirar el futuro: el peso decidido en el día `t-1` captura el retorno del día `t` (`w_{t-1} · ret_t`). Esta convención SHALL ser verificable de extremo a extremo con una prueba de sesgo: una señal que mira el futuro produce un Sharpe absurdamente alto, y una que sólo mira el pasado produce un Sharpe modesto.

#### Scenario: Una señal que mira el futuro da Sharpe absurdo
- **WHEN** se corre el motor con una señal cuyo peso es el signo del retorno del día siguiente (mira el futuro)
- **THEN** el Sharpe resultante es absurdamente alto (p. ej. > 5); si no lo es, la convención de `shift` está rota en la dirección que oculta el bug

#### Scenario: Una señal que sólo mira el pasado da Sharpe modesto
- **WHEN** se corre el motor con una señal cuyo peso es el signo del retorno del día anterior (sólo mira el pasado)
- **THEN** el Sharpe resultante es modesto (p. ej. < 2); si es enorme, hay look-ahead
