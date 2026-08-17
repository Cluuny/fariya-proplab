## Why

El challenge de una cuenta de fondeo no es un problema de trading (maximizar Sharpe), sino un **problema de barrera con doble frontera**: `P(tocar +objetivo antes de −límite)`. Ninguna herramienta del mercado calcula esta probabilidad, y es la única métrica que realmente decide si vale la pena comprar un challenge (sección 2.1 y 3.4 del documento maestro). El Bloque A dejó `src/challenge.py` como stub; este change lo implementa. Es el núcleo diferenciador del sistema y el hito de las semanas 4-5.

## What Changes

- Se implementa `src/challenge.py` (hoy un stub `NotImplementedError`): un **simulador de barrera** que recibe la serie de retornos diarios netos de una estrategia (la que produce `engine.py`) más las reglas de la firma, y estima por simulación la probabilidad de pasar el challenge y el valor económico esperado.
- **Block bootstrap (NO i.i.d.)**: ~10.000 remuestreos **por bloques** que preservan autocorrelación y clustering de volatilidad. Es una decisión crítica, no un detalle: un bootstrap i.i.d. subestima la volatilidad realista y, como menos volatilidad sube `P(pasar)` (sección 2.1), produciría un `P(pasar)` optimista y falso. El tamaño de bloque es configurable.
- **Reglas de la firma parametrizadas** (no se hardcodea ninguna firma: el documento avisa que cambian seguido): objetivo fase 1, objetivo fase 2, límite de pérdida diaria, drawdown máximo **estático** (no trailing — sección 2.2), y número de payouts `N` para el cálculo de quemar cuenta.
- **Salidas del simulador** (sección 3.4): `P(fase 1)`, `P(fase 2)`, `P(ambas)`; días esperados hasta pasar; `P(quemar la cuenta fondeada antes del payout N)`; **valor esperado neto de cuotas** (la métrica que decide); y la **curva `P(pasar)` frente a apalancamiento** para hallar el multiplicador óptimo.
- Se añaden a `src/config.py` los parámetros de la firma y del simulador (objetivos, límites, tamaño de bloque, `n_bootstraps`, `N` payouts, semilla).
- Integración opcional con `report.py` para incluir los resultados del simulador en el reporte de una estrategia.

Fuera de alcance (changes posteriores): estrategias reales H001–H005 (Bloque C) y el Flujo 2. El simulador se prueba aquí con retornos sintéticos y con la señal buy & hold existente, no con estrategias nuevas.

## Capabilities

### New Capabilities
- `challenge-simulator`: Estima por block-bootstrap la probabilidad de pasar un challenge de fondeo (problema de barrera con doble frontera) y el valor económico esperado, con reglas de firma parametrizadas y una curva de apalancamiento óptimo; verificado contra la fórmula analítica cerrada de primer paso.

### Modified Capabilities
<!-- Ninguna con cambio de comportamiento a nivel spec. La integración con `report.py` es glue de implementación, no un requisito nuevo de la capability `reporting`. -->

## Impact

- **Código**: `src/challenge.py` (implementación completa), `src/config.py` (parámetros de firma y simulador), `src/report.py` (integración opcional), `tests/test_challenge.py`.
- **Dependencias**: solo `numpy`/`pandas` ya presentes; el block bootstrap se implementa a mano (ninguna librería calcula `P(pasar)`).
- **Reproducibilidad**: el simulador usa una semilla configurable para que los resultados sean deterministas.
- **Reglas duras heredadas**: drawdown estático (no trailing); el simulador consume los retornos netos de `engine.py` (único punto de costos) sin recalcular costos.
