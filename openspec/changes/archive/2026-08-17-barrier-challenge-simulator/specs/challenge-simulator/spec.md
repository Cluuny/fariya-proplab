## Purpose

El simulador de barrera estima, por remuestreo de los retornos de una estrategia, la probabilidad de pasar un challenge de cuenta de fondeo y su valor económico esperado. El challenge es un problema de primer paso con doble barrera, no un problema de trading; esta capability es el núcleo que convierte retornos en el veredicto `P(pasar)`.

## ADDED Requirements

### Requirement: Estimación de probabilidad de pasar por fases

El sistema SHALL estimar, a partir de una serie de retornos diarios netos y de las reglas de la firma, la probabilidad de alcanzar el objetivo de cada fase antes de violar el límite de pérdida diaria o el drawdown máximo. SHALL reportar `P(pasar fase 1)`, `P(pasar fase 2)` y `P(pasar ambas)`.

#### Scenario: Reporta las tres probabilidades
- **WHEN** se corre el simulador con una serie de retornos y reglas de dos fases
- **THEN** devuelve `P(fase 1)`, `P(fase 2)` y `P(ambas)`, cada una en el rango [0, 1]

#### Scenario: El drawdown máximo es estático, no trailing
- **WHEN** la equity de una trayectoria simulada sube y luego cae
- **THEN** la violación de drawdown se evalúa contra el capital inicial (barrera estática), no contra un pico móvil (trailing)

### Requirement: Remuestreo por bloques que preserva la estructura temporal

El sistema SHALL generar las trayectorias simuladas mediante remuestreo por bloques (block bootstrap) de los retornos, con un tamaño de bloque configurable, de modo que se preserven la autocorrelación y el clustering de volatilidad. El sistema SHALL NOT usar remuestreo i.i.d. (bloque de tamaño 1) como método por defecto.

#### Scenario: El tamaño de bloque es configurable y mayor que 1 por defecto
- **WHEN** se inspecciona la configuración del simulador
- **THEN** el tamaño de bloque es un parámetro y su valor por defecto es mayor que 1

#### Scenario: El remuestreo por bloques preserva volatilidad agrupada
- **WHEN** la serie de entrada tiene clustering de volatilidad y se remuestrea por bloques suficientemente largos
- **THEN** la volatilidad realizada media de las trayectorias simuladas se aproxima a la de la serie original, no a la de un remuestreo i.i.d. que la destruiría

### Requirement: Reglas de la firma parametrizadas

El sistema SHALL aceptar las reglas de la firma como parámetros y NO hardcodear ninguna firma concreta. Como mínimo: objetivo de fase 1, objetivo de fase 2, límite de pérdida diaria, drawdown máximo y número de payouts `N`.

#### Scenario: Cambiar las reglas cambia el resultado
- **WHEN** se corre el simulador dos veces sobre la misma serie con objetivos o límites distintos
- **THEN** las probabilidades estimadas difieren de forma coherente con las reglas dadas

### Requirement: Métricas económicas del challenge

El sistema SHALL estimar los días esperados hasta pasar, la probabilidad de quemar la cuenta fondeada antes del payout `N`, y el **valor esperado neto de cuotas** del challenge (ingreso esperado menos costo de las cuotas ponderado por probabilidad de fallo).

#### Scenario: Reporta las métricas económicas
- **WHEN** se corre el simulador con el costo de la cuota y `N` payouts
- **THEN** devuelve días esperados hasta pasar, `P(quemar antes del payout N)` y el valor esperado neto de cuotas

### Requirement: Curva de probabilidad frente a apalancamiento

El sistema SHALL calcular la curva de `P(pasar)` en función del multiplicador de apalancamiento aplicado a los retornos, e identificar el apalancamiento que maximiza `P(pasar)`.

#### Scenario: El óptimo no es el apalancamiento máximo
- **WHEN** se calcula la curva `P(pasar)` vs apalancamiento sobre una estrategia con deriva positiva y volatilidad no nula
- **THEN** el apalancamiento que maximiza `P(pasar)` es estrictamente menor que el máximo del rango evaluado

### Requirement: Verificación contra la solución analítica cerrada

El sistema SHALL reproducir, sobre retornos sintéticos, la solución analítica cerrada del problema de primer paso con doble barrera dentro de una tolerancia. Para deriva cero y barreras simétricas, `P(pasar)` SHALL aproximarse a 0.5.

#### Scenario: Deriva cero y barreras simétricas dan P≈0.5
- **WHEN** se corre el simulador sobre retornos sintéticos de media cero con barreras simétricas (p. ej. 10/10)
- **THEN** `P(pasar)` estimada está dentro de la tolerancia de 0.5

#### Scenario: Coincide con la fórmula cerrada para deriva no nula
- **WHEN** se corre el simulador sobre retornos sintéticos con deriva y volatilidad conocidas y barreras dadas
- **THEN** `P(pasar)` estimada coincide, dentro de tolerancia, con `P = [1 − e^(−2μb/σ²)] / [1 − e^(−2μ(a+b)/σ²)]`

### Requirement: Determinismo bajo semilla fija

El sistema SHALL producir resultados deterministas dada una semilla fija: dos ejecuciones con la misma serie, reglas y semilla producen las mismas estimaciones.

#### Scenario: Misma semilla, mismo resultado
- **WHEN** se corre el simulador dos veces con idénticas entradas y la misma semilla
- **THEN** las métricas estimadas son idénticas
