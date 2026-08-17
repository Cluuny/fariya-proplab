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

El sistema SHALL garantizar que, en cada fecha, la suma de los valores absolutos de los pesos objetivo devueltos por una función de señal conforme no exceda 1 (`sum(|pesos|) <= 1`).

#### Scenario: Se rechaza exposición mayor a 1
- **WHEN** se valida la salida de una función de señal cuya suma de pesos absolutos en alguna fecha excede 1
- **THEN** la validación falla e identifica la(s) fecha(s) infractora(s)

#### Scenario: Se acepta exposición conforme
- **WHEN** se valida la salida de una función de señal cuya suma de pesos absolutos es menor o igual a 1 en todas las fechas
- **THEN** la validación pasa

### Requirement: Señal de referencia buy & hold

El sistema SHALL proveer una señal de referencia buy & hold conforme al contrato, que mantiene una exposición constante y sirve para verificar el motor de backtest de extremo a extremo.

#### Scenario: Buy & hold produce pesos constantes conformes
- **WHEN** se aplica la señal buy & hold a una serie de precios de un instrumento
- **THEN** devuelve pesos constantes en el tiempo que satisfacen el invariante `sum(|pesos|) <= 1`
