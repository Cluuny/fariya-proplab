## MODIFIED Requirements

### Requirement: Métricas económicas del challenge

El sistema SHALL estimar los días esperados hasta pasar y la probabilidad de quemar la cuenta fondeada antes del payout `N`, todo **condicionado a la absorción** (nunca tratando SIN ABSORBER como fallo). El sistema SHALL NOT reportar un número de valor económico hasta que el objetivo de decisión esté definido (objetivo umbral, sem 9-10): reporta sólo las primitivas honestas (P condicional a absorción, `P(quemar)`), en vez de un valor por unidad de tiempo mal especificado (el valor provisional asumía reingreso ilimitado a la cuota y su óptimo caía en el borde del grid). En particular:

- La probabilidad de pasar de decisión SHALL ser condicional a absorción: `p_cond = p_pasar / (p_pasar + p_fallar)` por fase.
- `P(quemar)` SHALL basarse en NO tocar la barrera de pérdida (complemento de FALLA) y SHALL crecer con el apalancamiento.
- Los días esperados SHALL incluir el tiempo de los intentos fallidos (día de absorción de PASADAS y QUEMADAS).
- Si la fracción SIN ABSORBER excede un umbral (p. ej. 5%) en alguna fase, el sistema SHALL marcar "horizonte insuficiente" y los **días esperados** y el **valor económico** SHALL ser `nan` (una estimación condicionada al pequeño subconjunto que absorbió sería sesgada).

#### Scenario: Reporta las métricas económicas
- **WHEN** se corre el simulador con horizonte suficiente (fracción sin absorber baja)
- **THEN** devuelve días esperados hasta pasar (incluyendo intentos fallidos), `P(quemar)` y la probabilidad condicional a absorción, sin un número de valor económico

#### Scenario: P(quemar) crece con el apalancamiento
- **WHEN** se compara `P(quemar la cuenta fondeada)` a mayor y menor apalancamiento sobre la misma estrategia
- **THEN** `P(quemar)` es mayor a mayor apalancamiento

#### Scenario: Horizonte insuficiente no produce un número engañoso
- **WHEN** una fase deja una fracción SIN ABSORBER por encima del umbral
- **THEN** el sistema marca "horizonte insuficiente" y tanto los días esperados como el valor económico son `nan` (no un número sesgado)

### Requirement: Curva de probabilidad frente a apalancamiento

El sistema SHALL reportar la curva de probabilidad de pasar **condicional a absorción** vs apalancamiento (monótona decreciente con horizonte honesto — la tesis §2.1) y opcionalmente la de `P(quemar)`. El sistema SHALL NOT reportar una curva de valor económico mal especificada ni colapsar a un único `optimal_leverage`: `optimal_leverage` SHALL ser `None` con un motivo explícito hasta que el objetivo de decisión esté definido.

**OBJETIVO COMPROMETIDO (sem 9-10) — objetivo UMBRAL:** el objetivo de decisión NO es maximizar valor esperado (que con dinero de la casa premia apalancar al máximo), sino un problema de umbral alineado con §1.2: `maximizar P(ingreso mensual ≥ $2500 sostenido durante 24 meses)`. Es un problema de barrera con óptimo interior natural (apalancar de más falla el umbral por quema; de menos, por payouts insuficientes) y hace endógeno el número de cuentas a escalar (decisión sem 11). Respaldo mínimo: `max valor/año s.a. P(quemar) ≤ umbral`.

**INVARIANTE (test es tarea de sem 9-10):** una vez definido el objetivo, si el óptimo cae en un borde del grid, el objetivo está mal especificado → error. Este test NO puede existir mientras `optimal_leverage` sea `None` (está vacío por construcción); NO se considera cerrado.

#### Scenario: P(pasar) crece al bajar el apalancamiento
- **WHEN** se calcula la curva de probabilidad condicional a absorción vs apalancamiento sobre una estrategia con deriva positiva y horizonte honesto
- **THEN** la probabilidad es mayor a menor apalancamiento (tendencia monótona decreciente en el apalancamiento)

#### Scenario: El apalancamiento de decisión sale del valor económico
- **WHEN** se consulta `optimal_leverage` antes de que el objetivo umbral esté definido (estado actual)
- **THEN** devuelve `None` con un motivo explícito, y NO se reporta una curva de valor económico mal especificada

#### Scenario: El óptimo no es el apalancamiento máximo
- **WHEN** el objetivo umbral (una vez definido, sem 9-10) produce un óptimo pegado a un borde del grid
- **THEN** se trata como una mala especificación del objetivo (error), no como un resultado válido; su test es tarea de esa fase
