## MODIFIED Requirements

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
