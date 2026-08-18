## ADDED Requirements

### Requirement: Ninguna métrica pliega "sin absorber" en fallo

El sistema SHALL garantizar que ninguna métrica reportada —probabilidad de decisión, número esperado de intentos, valor esperado neto, probabilidad de quema, días esperados, o apalancamiento óptimo— trate una trayectoria SIN ABSORBER como fallo, ni directa ni indirectamente. Una trayectoria que no tocó ninguna barrera dentro del horizonte NO es un fracaso; es una estimación incompleta.

#### Scenario: La probabilidad de decisión es invariante al horizonte
- **WHEN** se estima la probabilidad de pasar (condicional a absorción) de una misma estrategia con dos horizontes distintos, ambos con fracción sin absorber baja
- **THEN** las dos estimaciones coinciden dentro de la tolerancia de Monte Carlo (mientras que un `p_both` crudo que cuenta sin-absorber como no-paso SÍ cambiaría con el horizonte)

#### Scenario: Ninguna métrica derivada cuenta las sin-absorber como cuotas perdidas
- **WHEN** una fracción de trayectorias no absorbe dentro del horizonte
- **THEN** el número esperado de intentos y el valor esperado neto no cuentan esas trayectorias como intentos fallidos que requieren pagar una nueva cuota

## MODIFIED Requirements

### Requirement: Métricas económicas del challenge

El sistema SHALL estimar los días esperados hasta pasar, la probabilidad de quemar la cuenta fondeada antes del payout `N`, y el valor económico del challenge, todo **condicionado a la absorción** (nunca tratando SIN ABSORBER como fallo). En particular:

- La probabilidad de pasar de decisión SHALL ser condicional a que la trayectoria absorbió: `p_cond = p_pasar / (p_pasar + p_fallar)` por fase; el número esperado de intentos SHALL ser `1 / (p_cond1 · p_cond2)`.
- La probabilidad de quemar la cuenta fondeada SHALL basarse en NO tocar la barrera de pérdida (complemento de FALLA), no en alcanzar el objetivo; `P(quemar)` SHALL crecer con el apalancamiento.
- Los días esperados SHALL incluir el tiempo consumido por los intentos fallidos (no sólo el de las ganadoras), registrando el día de absorción tanto para PASADAS como para QUEMADAS.
- El valor económico SHALL expresarse como **valor por unidad de tiempo**, y el `payout` esperado por ciclo SHALL derivarse simulando la fase fondeada (proporción de reparto × retorno esperado condicionado a sobrevivir), NO fijarse como constante independiente del apalancamiento.
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
