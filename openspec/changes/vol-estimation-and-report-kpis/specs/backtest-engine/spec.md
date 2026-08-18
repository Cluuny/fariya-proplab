## ADDED Requirements

### Requirement: Estimación de volatilidad segura ante huecos

El sistema SHALL proveer una estimación de volatilidad por instrumento que se calcule sobre los **días de cotización propios** de cada instrumento, excluyendo los retornos cero que el forward-fill inyecta en los huecos de calendario. En un DataFrame combinado, un índice tiene retorno cero cada día que un par de FX cotizó pero él no; incluir esos ceros **deflacta** su vol estimada (~20%) y sobredimensionaría los índices en un sizing por volatilidad inversa. El sizing por vol inversa SHALL usar esta estimación, no la volatilidad de la serie de retornos con ceros de relleno.

Nota: el forward-fill también extendería el último precio si una serie termina antes que las otras (cola). Hoy no aplica (todas las series cierran en la misma fecha), pero es una limitación conocida al añadir un instrumento de historia más corta.

#### Scenario: La vol de un índice con huecos no se deflacta
- **WHEN** se estima la volatilidad de un índice que no cotiza en una fracción de los días del DataFrame combinado
- **THEN** la estimación se aproxima a la vol calculada sobre los días de cotización propios del índice, no a la vol deflactada por los ceros de relleno

## MODIFIED Requirements

### Requirement: Reproducción de un Sharpe histórico conocido

El sistema SHALL verificar el motor contra un Sharpe de referencia de un índice, **nombrando con precisión qué es externo y qué es interno**. La verificación EXTERNA SHALL ser que la serie de precios ES el índice: sus endpoints (al menos el inicial, idealmente también el final) coinciden con los cierres públicos del índice. Si la serie es el índice, su Sharpe es el del índice **por construcción** — esto NO es una comparación contra una cifra publicada ni un paper. El acuerdo entre el Sharpe geométrico (CAGR/vol) y el de `engine.sharpe` (media aritmética) sobre la misma serie es un cross-check **interno** entre estimadores, no una verificación externa. El motor SHALL reproducir el Sharpe de referencia dentro de la tolerancia acordada.

#### Scenario: Buy & hold reproduce el Sharpe del índice
- **WHEN** se corre el motor con la señal buy & hold sobre la serie histórica de un índice cuyos endpoints coinciden con los cierres públicos del índice
- **THEN** el Sharpe calculado por el motor coincide con el de referencia dentro de la tolerancia, y la procedencia distingue la verificación externa (la serie es el índice) del cross-check interno (geométrico vs aritmético)
