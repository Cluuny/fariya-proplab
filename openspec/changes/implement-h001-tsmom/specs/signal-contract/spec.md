## ADDED Requirements

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
