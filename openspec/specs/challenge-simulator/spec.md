# challenge-simulator Specification

## Purpose

El simulador de barrera estima, por remuestreo de los retornos de una estrategia, la probabilidad de pasar un challenge de cuenta de fondeo y su valor económico esperado. El challenge es un problema de primer paso con doble barrera, no un problema de trading; esta capability es el núcleo que convierte retornos en el veredicto `P(pasar)`.

## Requirements

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

El sistema SHALL estimar los días esperados hasta pasar, la probabilidad de quemar la cuenta fondeada antes del payout `N`, y el valor económico del challenge, todo **condicionado a la absorción** (nunca tratando SIN ABSORBER como fallo). En particular:

- La probabilidad de pasar de decisión SHALL ser condicional a que la trayectoria absorbió: `p_cond = p_pasar / (p_pasar + p_fallar)` por fase; el número esperado de intentos SHALL ser `1 / (p_cond1 · p_cond2)`.
- La probabilidad de quemar la cuenta fondeada SHALL basarse en NO tocar la barrera de pérdida (complemento de FALLA), no en alcanzar el objetivo; `P(quemar)` SHALL crecer con el apalancamiento.
- Los días esperados SHALL incluir el tiempo consumido por los intentos fallidos (no sólo el de las ganadoras), registrando el día de absorción tanto para PASADAS como para QUEMADAS.
- El valor económico SHALL expresarse como valor por unidad de tiempo, y el `payout` esperado por ciclo SHALL derivarse simulando la fase fondeada (proporción de reparto × retorno esperado condicionado a sobrevivir), NO fijarse como constante independiente del apalancamiento.
- Si la fracción SIN ABSORBER excede un umbral (p. ej. 5%) en alguna fase, el sistema SHALL marcar "horizonte insuficiente" y NO reportar un valor económico (devolver `nan`/bandera) en vez de un número engañoso.

#### Scenario: Reporta las métricas económicas
- **WHEN** se corre el simulador con horizonte suficiente (fracción sin absorber baja) y payout derivado de la fase fondeada
- **THEN** devuelve días esperados hasta pasar (incluyendo intentos fallidos), `P(quemar)` y el valor por unidad de tiempo, todos condicionados a absorción

#### Scenario: P(quemar) crece con el apalancamiento
- **WHEN** se compara `P(quemar la cuenta fondeada)` a mayor y menor apalancamiento sobre la misma estrategia
- **THEN** `P(quemar)` es mayor a mayor apalancamiento

#### Scenario: Horizonte insuficiente no produce un número engañoso
- **WHEN** una fase deja una fracción SIN ABSORBER por encima del umbral
- **THEN** el sistema marca "horizonte insuficiente" y no reporta un valor económico numérico para esa configuración

### Requirement: Contabilidad de tres resultados

El sistema SHALL clasificar cada trayectoria simulada en exactamente uno de tres resultados mutuamente excluyentes: **PASÓ** (alcanzó el objetivo antes que cualquier barrera de pérdida), **FALLÓ** (tocó el límite de pérdida diaria o el drawdown máximo estático), o **SIN ABSORBER** (llegó al final del horizonte sin tocar ninguna barrera). El sistema SHALL NOT contabilizar "SIN ABSORBER" como fallo. SHALL reportar `P(pasar)`, `P(fallar)` y `P(sin absorber)` por separado, y SHALL exponer el horizonte usado.

#### Scenario: Los tres resultados suman 1 y sin-absorber es visible
- **WHEN** se corre el simulador con retornos de baja deriva y un horizonte corto que deja muchas trayectorias sin absorber
- **THEN** `P(pasar) + P(fallar) + P(sin absorber) == 1` (dentro de tolerancia numérica) y `P(sin absorber)` es estrictamente mayor que cero

#### Scenario: Sin absorber no se pliega en fallo
- **WHEN** una trayectoria llega al final del horizonte sin haber tocado el objetivo ni ninguna barrera de pérdida
- **THEN** se contabiliza como SIN ABSORBER, no como FALLÓ, y no reduce `P(pasar)` por vía de contabilizarse como fracaso

#### Scenario: El horizonte es explícito en el resultado
- **WHEN** se inspecciona el resultado del simulador
- **THEN** el horizonte (en días) usado para la clasificación está disponible en el resultado

### Requirement: Ninguna métrica pliega "sin absorber" en fallo

El sistema SHALL garantizar que ninguna métrica reportada —probabilidad de decisión, número esperado de intentos, valor esperado neto, probabilidad de quema, días esperados, o apalancamiento óptimo— trate una trayectoria SIN ABSORBER como fallo, ni directa ni indirectamente. Una trayectoria que no tocó ninguna barrera dentro del horizonte NO es un fracaso; es una estimación incompleta.

#### Scenario: La probabilidad de decisión es invariante al horizonte
- **WHEN** se estima la probabilidad de pasar (condicional a absorción) de una misma estrategia con dos horizontes distintos, ambos con fracción sin absorber baja
- **THEN** las dos estimaciones coinciden dentro de la tolerancia de Monte Carlo (mientras que un `p_both` crudo que cuenta sin-absorber como no-paso SÍ cambiaría con el horizonte)

#### Scenario: Ninguna métrica derivada cuenta las sin-absorber como cuotas perdidas
- **WHEN** una fracción de trayectorias no absorbe dentro del horizonte
- **THEN** el número esperado de intentos y el valor esperado neto no cuentan esas trayectorias como intentos fallidos que requieren pagar una nueva cuota

### Requirement: Curva de probabilidad frente a apalancamiento

El sistema SHALL reportar SIEMPRE dos curvas diagnósticas vs apalancamiento: la probabilidad de pasar **condicional a absorción** (monótona decreciente en el apalancamiento con horizonte honesto — la tesis §2.1) y el valor por unidad de tiempo (provisional). El sistema SHALL NOT colapsar ninguna de las dos en un único `optimal_leverage` en este estado: sobre `P(pasar)` sola el óptimo es un mínimo degenerado, y el objetivo de valor no está definido hasta modelar la fase fondeada. `optimal_leverage` SHALL devolver `None` con un motivo explícito hasta entonces.

**DECISIÓN (sem 6):** `optimal_leverage = None` hasta que la fase fondeada esté modelada. Alternativas rechazadas y por qué:
- `argmax P(pasar)` → mínimo degenerado (§2.1).
- `min k factible` (menor apalancamiento que pasa el guard) → `horizon_days` y `leverage_min` se vuelven perillas ocultas; a horizonte creciente converge al mínimo del grid.
- growth-optimal / log-utility → ignora que el drawdown es una barrera absorbente; sobre-apalanca sistemáticamente.

**OBJETIVO COMPROMETIDO (sem 9-10):** valor esperado por unidad de tiempo, con `payout` por ciclo **endógeno** al apalancamiento (derivado de simular la fase fondeada). El óptimo interior emerge del tira y afloja real (ingreso que crece con `k` vs. probabilidad de quema que crece más rápido), sin perillas inventadas.

**INVARIANTE:** una vez definido el objetivo, si el óptimo cae en un borde del grid, el objetivo está mal especificado → error, no resultado.

#### Scenario: P(pasar) crece al bajar el apalancamiento
- **WHEN** se calcula la curva de probabilidad condicional a absorción vs apalancamiento sobre una estrategia con deriva positiva y horizonte honesto
- **THEN** la probabilidad es mayor a menor apalancamiento (tendencia monótona decreciente en el apalancamiento)

#### Scenario: El apalancamiento de decisión sale del valor económico
- **WHEN** se consulta `optimal_leverage` antes de que la fase fondeada esté modelada (estado actual)
- **THEN** devuelve `None` con un motivo explícito, y se reportan ambas curvas diagnósticas; NO se colapsa a un número que una perilla de modelado determinaría

#### Scenario: El óptimo no es el apalancamiento máximo
- **WHEN** el objetivo de decisión (una vez definido, sem 9-10) produce un óptimo pegado a un borde del grid (mínimo o máximo)
- **THEN** se trata como una mala especificación del objetivo (error), no como un resultado válido

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
