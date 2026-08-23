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
