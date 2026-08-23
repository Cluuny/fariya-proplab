## MODIFIED Requirements

### Requirement: Cálculo de retornos netos con costos

El sistema SHALL recibir un DataFrame de pesos objetivo y una serie de precios, y devolver una serie de retornos netos que incorpore comisión, spread, slippage, impacto y **swap** (cargo de mantener posición). El motor SHALL ser el único módulo del sistema que aplica costos de operación.

El **swap** SHALL ser DIRECCIONAL y SHALL separar dos componentes, ambos aplicados sobre la posición mantenida (el peso del día previo), no sobre el turnover:
- **`carry`** — el diferencial de tasas diario CON SIGNO que una posición LARGA gana (`+` = la larga cobra, `−` = la larga paga); una posición CORTA gana `−carry`. Es un término de P&L, NO un costo: en una cartera long/short se cancela parcialmente y puede ser ingreso neto.
- **`swap_margin`** — el margen del broker, SIEMPRE un costo sobre `|peso|/día` (unidireccional). Es lo que NO se cancela en una cartera balanceada.

El motor SHALL aplicar `swap_cost = swap_margin·|w_prev| − carry·w_prev` por instrumento. Los parámetros SHALL calibrarse contra fuentes reales publicadas, documentadas con fuente y fecha (tasas de política para el `carry`; tabla long/short de un broker para el `swap_margin`), NO inventadas.

**LIMITACIÓN CONOCIDA — snapshot fechado:** los swaps son dinámicos (cambian a diario); la calibración es un snapshot con fecha (ver `config` SWAP_CALIBRATION). La tabla long/short por instrumento del broker refinaría el margen por instrumento.

#### Scenario: Una posición larga con carry positivo RECIBE swap
- **WHEN** se mantiene una posición larga en un instrumento con `carry > 0` y `swap_margin = 0`, sin movimiento de precio
- **THEN** el retorno neto diario es positivo e igual a `+carry` (la larga cobra el diferencial), y una posición corta idéntica rinde `−carry`

#### Scenario: El margen del broker siempre resta
- **WHEN** se mantiene una posición (larga o corta) con `swap_margin > 0`
- **THEN** el margen resta en ambos lados, proporcional a `|peso|` (unidireccional)

#### Scenario: Una cartera que cosecha carry cuesta menos que el modelo unsigned
- **WHEN** se corre una cartera long/short alineada con el carry (larga el de carry positivo, corta el de carry negativo) con el modelo direccional
- **THEN** el costo total de swap es MENOR que con el modelo unsigned (margen sobre `|peso|` en ambos lados sin compensación de carry), porque el carry se cobra como ingreso

#### Scenario: Los costos reducen el retorno
- **WHEN** se corre el motor con costos positivos sobre una estrategia que rota posiciones
- **THEN** el retorno neto acumulado es estrictamente menor que el retorno bruto de la misma estrategia sin costos

#### Scenario: Sin rotación, sólo costo de mantener
- **WHEN** se corre el motor sobre una estrategia buy & hold que no rota posiciones tras la entrada inicial
- **THEN** los costos de transacción (turnover) posteriores a la entrada son cero, pero el swap (margen ∓ carry) se acumula cada día que se mantiene la posición

#### Scenario: El swap escala con los días mantenidos
- **WHEN** se comparan dos posiciones idénticas mantenidas por distinto número de días
- **THEN** el componente de margen del swap es mayor para la que se mantiene más días (proporcional a los días × `|peso|`)
