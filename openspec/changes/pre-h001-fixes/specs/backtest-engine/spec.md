## ADDED Requirements

### Requirement: Anualización consistente con el calendario observado

El sistema SHALL anualizar el Sharpe (y cualquier métrica anualizada) usando el número de barras por año **observado** en la serie, no una constante global fija. Series con distinto calendario (FX ~260/año, índices ~247/año tras descartar fines de semana) SHALL anualizarse cada una con su propio conteo, para no introducir un sesgo sistemático.

#### Scenario: El Sharpe se anualiza con las barras/año de la serie
- **WHEN** se calcula el Sharpe de dos series con distinto número de barras por año
- **THEN** cada una se anualiza con su propio conteo observado de barras por año, no con un factor común fijo

## MODIFIED Requirements

### Requirement: Cálculo de retornos netos con costos

El sistema SHALL recibir un DataFrame de pesos objetivo y una serie de precios, y devolver una serie de retornos netos que incorpore comisión, spread, slippage, impacto y **swap** (cargo de mantener posición). El motor SHALL ser el único módulo del sistema que aplica costos de operación. El swap SHALL aplicarse como un cargo **diario proporcional a `|peso|`** de la posición mantenida (no al turnover), de modo que una estrategia de holding largo (que rota poco pero mantiene semanas) incurra el costo real de mantener.

#### Scenario: Los costos reducen el retorno
- **WHEN** se corre el motor con costos positivos sobre una estrategia que rota posiciones
- **THEN** el retorno neto acumulado es estrictamente menor que el retorno bruto de la misma estrategia sin costos

#### Scenario: Sin rotación, sólo costo de mantener
- **WHEN** se corre el motor sobre una estrategia buy & hold que no rota posiciones tras la entrada inicial
- **THEN** los costos de **transacción** (turnover) posteriores a la entrada son cero, pero el **swap** se acumula cada día que se mantiene la posición, proporcional a `|peso|`

#### Scenario: El swap escala con los días mantenidos
- **WHEN** se comparan dos posiciones idénticas mantenidas por distinto número de días
- **THEN** el costo de swap total es mayor para la que se mantiene más días (proporcional a los días × `|peso|`)
