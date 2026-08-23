## MODIFIED Requirements

### Requirement: Cálculo de retornos netos con costos

El sistema SHALL recibir un DataFrame de pesos objetivo y una serie de precios, y devolver una serie de retornos netos que incorpore comisión, spread, slippage, impacto y **swap** (cargo de mantener posición). El motor SHALL ser el único módulo del sistema que aplica costos de operación.

El **swap** SHALL ser DIRECCIONAL y SHALL separar dos componentes, ambos aplicados sobre la posición mantenida (el peso del día previo), no sobre el turnover:
- **`carry`** — el diferencial de tasas diario CON SIGNO que una posición LARGA gana (`+` = la larga cobra, `−` = la larga paga); una posición CORTA gana `−carry`. Es un término de P&L, NO un costo: en una cartera long/short se cancela parcialmente y puede ser ingreso neto. El `carry` SHALL ser HISTÓRICO (variar con la fecha según las tasas de política vigentes en cada momento), NO un snapshot: el motor SHALL aceptar una MATRIZ carry fecha×instrumento. Aplicar un snapshot actual a todo el histórico es un sesgo con información del presente (el signo del diferencial se invierte en partes de la muestra).
- **`swap_margin`** — el margen del broker, SIEMPRE un costo sobre `|peso|/día` (unidireccional).

Ambos componentes SHALL escalarse por el factor de convención de días de cotización (365/261 ≈ 1.40): el broker cobra 365 días de swap repartidos en ~261 sesiones (swap triple del miércoles), y el motor sólo aplica el cargo en días de cotización. El motor SHALL aplicar `swap_cost = swap_margin·|w_prev| − carry_t·w_prev`. Los parámetros SHALL calibrarse contra fuentes reales publicadas, documentadas con fuente y fecha (series históricas de tasas de política para el `carry`; tabla long/short de un broker para el `swap_margin`), NO inventadas.

**LIMITACIÓN CONOCIDA:** el margen y los dividend yields de índices son snapshots fechados; sólo el `carry` de tasas es histórico. Los div yields se mantienen constantes (efecto de 2º orden).

#### Scenario: El carry es histórico y su signo puede invertirse
- **WHEN** se computa la matriz de carry de un par (p. ej. EURUSD) sobre 2004-2026 con tasas de política históricas
- **THEN** el carry varía con la fecha y es POSITIVO en períodos donde la tasa base superó a la quote (EURUSD en 2009-2015), no un valor constante del snapshot actual

#### Scenario: Convención de días de cotización
- **WHEN** se aplica el swap sobre una posición mantenida
- **THEN** carry y margen incluyen el factor 365/261, de modo que el total anual sobre ~261 sesiones equivale a 365 días de swap

#### Scenario: Una posición larga con carry positivo RECIBE swap
- **WHEN** se mantiene una posición larga en un instrumento con `carry > 0` y `swap_margin = 0`, sin movimiento de precio
- **THEN** el retorno neto diario es positivo (la larga cobra el diferencial), y una posición corta idéntica lo paga

#### Scenario: El margen del broker siempre resta
- **WHEN** se mantiene una posición (larga o corta) con `swap_margin > 0`
- **THEN** el margen resta en ambos lados, proporcional a `|peso|` (unidireccional)

#### Scenario: Una cartera que cosecha carry cuesta menos que el modelo unsigned
- **WHEN** se corre una cartera long/short alineada con el carry con el modelo direccional
- **THEN** el costo total de swap es MENOR que con el modelo unsigned (margen sobre `|peso|` sin compensación de carry)

#### Scenario: Los costos reducen el retorno
- **WHEN** se corre el motor con costos positivos sobre una estrategia que rota posiciones
- **THEN** el retorno neto acumulado es estrictamente menor que el retorno bruto de la misma estrategia sin costos

#### Scenario: Sin rotación, sólo costo de mantener
- **WHEN** se corre el motor sobre una estrategia buy & hold que no rota posiciones tras la entrada inicial
- **THEN** los costos de transacción (turnover) posteriores a la entrada son cero, pero el swap (margen ∓ carry) se acumula cada día que se mantiene la posición

#### Scenario: El swap escala con los días mantenidos
- **WHEN** se comparan dos posiciones idénticas mantenidas por distinto número de días
- **THEN** el componente de margen del swap es mayor para la que se mantiene más días (proporcional a los días × `|peso|`)
