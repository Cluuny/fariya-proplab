## ADDED Requirements

### Requirement: Señal estacional turn-of-the-month (TOM)

El sistema SHALL proveer una señal `tom_seasonal` conforme al contrato de señal pura que implemente la hipótesis H003: estar **largo** en cada índice **sólo** durante la ventana de cambio de mes —los primeros 3 días hábiles del mes más el último día hábil del mes— y **flat** el resto. El tamaño SHALL ser por volatilidad inversa (`engine.rolling_vol`, gap-safe) con escalado global **ex-ante** hacia un objetivo de volatilidad de portafolio, acotado por `max_gross`. La señal SHALL ser long-only (pesos ≥ 0).

El constructor de pesos SHALL estar parametrizado por una máscara de días activos, de modo que un benchmark nulo (mismos instrumentos, mismo sizing, mismo número de días activos por mes, pero en días aleatorios) use EXACTAMENTE el mismo constructor y difiera sólo en qué días se activan.

#### Scenario: Activa sólo en la ventana de cambio de mes
- **WHEN** se aplica `tom_seasonal` sobre varios meses
- **THEN** los pesos son no-cero (largos) sólo en los primeros 3 días hábiles y el último día hábil de cada mes, y cero el resto de los días

#### Scenario: Long-only
- **WHEN** se computan los pesos de `tom_seasonal`
- **THEN** ningún peso es negativo en ninguna fecha

#### Scenario: El escalado a vol de portafolio es ex-ante (sin look-ahead)
- **WHEN** se computan los pesos y luego se recomputan sobre la misma serie extendida con fechas futuras adicionales
- **THEN** los pesos en las fechas originales no cambian (el escalar usa sólo volatilidad observada hasta cada fecha)

#### Scenario: Exposición bruta acotada
- **WHEN** se valida la salida de `tom_seasonal` con el `max_gross` del contrato
- **THEN** `sum(|pesos|) <= max_gross` en toda fecha
