## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: Curva de probabilidad frente a apalancamiento

El sistema SHALL calcular la curva de `P(pasar)` en función del multiplicador de apalancamiento aplicado a los retornos. Con un horizonte honesto (largo) y deriva positiva, esta curva es monótona decreciente en el apalancamiento: menos apalancamiento (menos volatilidad) implica mayor `P(pasar)`, consistente con la tesis de "mínima volatilidad, paciencia infinita" (documento §2.1). El apalancamiento **de decisión** SHALL determinarse maximizando el `valor esperado neto de cuotas` —que pone precio al tiempo y al capital inmovilizado del bajo apalancamiento—, NO maximizando `P(pasar)` (cuyo máximo caería en el apalancamiento mínimo).

#### Scenario: P(pasar) crece al bajar el apalancamiento
- **WHEN** se calcula la curva `P(pasar)` vs apalancamiento sobre una estrategia con deriva positiva y volatilidad no nula, con horizonte largo
- **THEN** `P(pasar)` es mayor a menor apalancamiento (tendencia monótona decreciente en el apalancamiento)

#### Scenario: El apalancamiento de decisión sale del valor económico
- **WHEN** se determina el apalancamiento óptimo de decisión
- **THEN** se elige el apalancamiento que maximiza el valor esperado neto de cuotas, no el que maximiza `P(pasar)`

#### Scenario: El óptimo no es el apalancamiento máximo
- **WHEN** se evalúa el apalancamiento de decisión sobre una estrategia con edge (valor esperado neto positivo en algún apalancamiento del rango)
- **THEN** el apalancamiento elegido es estrictamente menor que el máximo del rango evaluado

<!-- Nota: para una estrategia SIN edge (valor esperado negativo en todo el rango) no hay óptimo significativo; el criterio económico puede degenerar al extremo, lo cual es en sí una señal de que la estrategia no debe operarse. -->

