# signal-contract Specification

## Purpose

El contrato de señal define la frontera estable entre una hipótesis de trading y el resto del sistema: una función pura que traduce precios en pesos objetivo. Esta frontera es lo que permitirá que el futuro Flujo 2 genere código que encaje sin tocar el motor.

## Requirements

### Requirement: Contrato de función de señal pura

El sistema SHALL definir un contrato de señal como una función que recibe precios (y opcionalmente parámetros) y devuelve un DataFrame de pesos objetivo indexado por fecha, con una columna por instrumento. La función SHALL ser pura: no realiza I/O, no muta sus entradas, no mantiene estado entre llamadas, y para las mismas entradas produce siempre la misma salida.

#### Scenario: Determinismo y ausencia de efectos
- **WHEN** una función de señal se invoca dos veces con los mismos precios de entrada
- **THEN** devuelve pesos idénticos en ambas llamadas y las entradas quedan sin modificar

#### Scenario: Forma de la salida
- **WHEN** una función de señal recibe precios de M instrumentos a lo largo de T fechas
- **THEN** devuelve un DataFrame de pesos indexado por las fechas de entrada, con una columna por instrumento

### Requirement: Invariante de exposición acotada

El sistema SHALL garantizar que, en cada fecha, la suma de los valores absolutos de los pesos objetivo devueltos por una función de señal conforme no exceda un máximo de exposición bruta configurable `max_gross` (`sum(|pesos|) <= max_gross`), NO un tope fijo de 1. Estrategias con sizing por volatilidad inversa (como TSMOM sobre varios instrumentos) corren exposición bruta 2-4× de forma natural; forzar `<= 1` aplastaría la volatilidad por debajo del objetivo y rompería la comparación contra la literatura. La exposición absoluta / apalancamiento se controla aguas abajo (vol-targeting y el escalado de apalancamiento del simulador), no con un tope de 1 en el contrato de señal.

#### Scenario: Se rechaza exposición mayor a 1
- **WHEN** se valida la salida de una función de señal cuya suma de pesos absolutos en alguna fecha excede `max_gross`
- **THEN** la validación falla e identifica la(s) fecha(s) infractora(s)

#### Scenario: Se acepta exposición conforme
- **WHEN** se valida la salida de una función de señal cuya suma de pesos absolutos es menor o igual a `max_gross` en todas las fechas
- **THEN** la validación pasa

#### Scenario: TSMOM con vol-inversa (bruto 2-4×) es conforme
- **WHEN** se valida una señal de vol-inversa cuya exposición bruta típica es 2-4× pero no excede `max_gross`
- **THEN** la validación pasa (no se aplasta a 1)

### Requirement: Señal de referencia buy & hold

El sistema SHALL proveer una señal de referencia buy & hold conforme al contrato, que mantiene una exposición constante y sirve para verificar el motor de backtest de extremo a extremo.

#### Scenario: Buy & hold produce pesos constantes conformes
- **WHEN** se aplica la señal buy & hold a una serie de precios de un instrumento
- **THEN** devuelve pesos constantes en el tiempo que satisfacen el invariante `sum(|pesos|) <= 1`

### Requirement: Señal Time-Series Momentum (TSMOM)

El sistema SHALL proveer una señal `tsmom` conforme al contrato de señal pura que implemente la hipótesis H001: la dirección de cada instrumento es el **signo de su retorno a 12 meses de calendario** (long si > 0, short si < 0), calculado sobre el calendario propio del instrumento de forma segura ante huecos (el precio de hace 12 meses es el último disponible en o antes de esa fecha). El tamaño SHALL ser por **volatilidad inversa** (usando la estimación gap-safe `engine.rolling_vol`), con un escalado global **ex-ante** hacia un objetivo de volatilidad de portafolio, acotado por `max_gross`. El rebalanceo SHALL ser **mensual** (primer día hábil del mes), manteniendo los pesos entre rebalanceos.

#### Scenario: La dirección es el signo del retorno a 12 meses
- **WHEN** un instrumento tuvo un retorno positivo a 12 meses de calendario a una fecha de rebalanceo
- **THEN** su peso en esa fecha es largo (signo +), y corto si el retorno a 12 meses fue negativo

#### Scenario: El escalado a vol de portafolio es ex-ante (sin look-ahead)
- **WHEN** se computan los pesos de `tsmom` y luego se recomputan sobre la misma serie extendida con fechas futuras adicionales
- **THEN** los pesos en las fechas originales no cambian (el escalar en cada fecha usa sólo volatilidad observada hasta esa fecha, no la vol realizada de toda la serie)

#### Scenario: Rebalanceo mensual con holding
- **WHEN** se aplica `tsmom` sobre un tramo de varios meses
- **THEN** los pesos sólo cambian en el primer día hábil de cada mes y se mantienen constantes entre esas fechas

#### Scenario: Exposición bruta acotada
- **WHEN** se valida la salida de `tsmom` con el `max_gross` del contrato
- **THEN** `sum(|pesos|) <= max_gross` en toda fecha (el escalado que exceda el bruto se recorta ese día)
