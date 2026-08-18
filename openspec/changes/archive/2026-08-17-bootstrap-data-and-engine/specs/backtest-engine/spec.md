## Purpose

El motor de backtest traduce pesos objetivo en retornos netos aplicando los costos reales de operar (comisión, spread, slippage, impacto). Es el único componente que aplica costos, y su fidelidad es lo que separa una estrategia rentable de un espejismo.

## ADDED Requirements

### Requirement: Cálculo de retornos netos con costos

El sistema SHALL recibir un DataFrame de pesos objetivo y una serie de precios, y devolver una serie de retornos netos que incorpore comisión, spread, slippage e impacto. El motor SHALL ser el único módulo del sistema que aplica costos de operación.

#### Scenario: Los costos reducen el retorno
- **WHEN** se corre el motor con costos positivos sobre una estrategia que rota posiciones
- **THEN** el retorno neto acumulado es estrictamente menor que el retorno bruto de la misma estrategia sin costos

#### Scenario: Sin rotación, sólo costo de mantener
- **WHEN** se corre el motor sobre una estrategia buy & hold que no rota posiciones tras la entrada inicial
- **THEN** los costos de transacción posteriores a la entrada son cero y sólo se aplican los costos asociados a la posición inicial

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
