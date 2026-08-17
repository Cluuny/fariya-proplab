## Context

Ver `proposal.md` — Why. El Bloque A dejó una tubería funcional: `engine.py` produce una serie de retornos diarios netos, y `challenge.py` es un stub `NotImplementedError` con el contrato documentado. Este change implementa ese núcleo. Restricción conceptual clave (sección 2.1): el challenge es un problema de primer paso con doble barrera, y bajar la volatilidad **sube** `P(pasar)`; por eso el método de simulación no puede destruir la estructura de volatilidad de la serie.

## Goals / Non-Goals

**Goals:**
- Simulador de barrera por block bootstrap sobre retornos netos, con reglas de firma parametrizadas.
- Salidas: `P(fase1/2/ambas)`, días esperados, `P(quemar)`, valor esperado neto de cuotas, curva `P(pasar)` vs apalancamiento.
- Verificación matemática contra la fórmula cerrada de primer paso (deriva cero → P≈0.5).
- Determinismo bajo semilla.

**Non-Goals:**
- Estrategias reales H001–H005 (Bloque C) y Flujo 2.
- Modelar reglas idiosincráticas de una firma concreta (solo el conjunto mínimo parametrizado).
- Recalcular costos: el simulador consume los retornos netos de `engine.py` tal cual.
- Trailing drawdown: el documento exige drawdown estático (sección 2.2).

## Decisions

### D1 — Block bootstrap (moving-block), tamaño de bloque configurable, default > 1
Se remuestrean bloques contiguos de retornos (moving-block bootstrap) y se concatenan hasta la longitud del horizonte simulado. Preserva autocorrelación y clustering de volatilidad. **Alternativa:** bootstrap i.i.d. (bloque=1) — descartada como default: subestima la volatilidad realista y produce `P(pasar)` optimista y falso (sección 2.1). Se permite bloque=1 solo para tests de validación analítica (donde los retornos sintéticos SON i.i.d. por construcción).

### D2 — Barreras evaluadas trayectoria a trayectoria, drawdown estático
Cada trayectoria simulada se recorre día a día acumulando equity; se marca "pasa" al tocar el objetivo de fase y "quema" al violar el límite de pérdida diaria o el drawdown máximo medido **contra el capital inicial** (estático). El primer evento que ocurre define el resultado de esa trayectoria (first passage). **Alternativa:** fórmula analítica directa — se usa solo como *oráculo de verificación*, no como motor, porque no captura reglas discretas (límite diario, dos fases, payouts).

### D3 — Verificación contra la fórmula cerrada como test, no como implementación
El test de aceptación genera retornos sintéticos gaussianos i.i.d. con `μ`, `σ` conocidos y compara la `P(pasar)` simulada contra `P = [1 − e^(−2μb/σ²)] / [1 − e^(−2μ(a+b)/σ²)]`. Con `μ=0` y barreras simétricas, la fórmula da 0.5. Esto verifica el motor contra matemática, no contra intuición (sección 3.4). Tolerancia derivada del error de Monte Carlo (~`1/√n_bootstraps`).

### D4 — Valor esperado neto de cuotas
`E[neto] = P(ambas)·(payout_esperado) − E[nº de cuotas compradas]·(costo_cuota)`, donde el nº esperado de intentos se deriva de `P(ambas)` (geométrica) y `P(quemar)` acota el ingreso tras fondeo. La fórmula exacta se fija en implementación; el contrato de la spec es que la métrica exista y responda coherentemente a las reglas. Es la métrica que decide (sección 3.4).

### D5 — Apalancamiento como escalado de retornos
La curva `P(pasar)` vs leverage se obtiene escalando la serie de retornos por un multiplicador `k` sobre una malla y recomputando `P(pasar)`. El óptimo se localiza como el `argmax`. Para una estrategia con deriva positiva y `σ>0`, el óptimo es interior (< máximo del rango): más leverage sube el objetivo alcanzable pero también la probabilidad de tocar el límite antes (sección 2.1). **Alternativa:** derivar el óptimo analíticamente — descartada; la malla es robusta a las reglas discretas.

### D6 — Parámetros en `config.py` como dataclass de reglas de firma
Se añade una `dataclass FirmRules` (objetivos, límite diario, DD, `N` payouts, costo cuota) y parámetros del simulador (`block_size`, `n_bootstraps`, `horizon_days`, `seed`), versionados como el resto de la configuración (coherente con la decisión D6 del Bloque A).

## Risks / Trade-offs

- **Costo computacional de 10.000 bootstraps × malla de leverage** → Mitigación: vectorizar con numpy (simular todas las trayectorias como matriz), y usar una malla de leverage moderada; exponer `n_bootstraps` para bajarlo en tests.
- **Elección del tamaño de bloque sesga el resultado** (muy corto destruye volatilidad, muy largo reduce la diversidad del remuestreo) → Mitigación: default razonable (p. ej. ~20 días ≈ 1 mes de trading) documentado y configurable; se puede barrer en análisis posterior.
- **La fórmula cerrada asume proceso continuo (browniano)**; la simulación es discreta y con reglas extra → Mitigación: el test de verificación usa retornos i.i.d. gaussianos de σ pequeña y barreras en múltiplos de σ para acercarse al límite continuo, con tolerancia de Monte Carlo.
- **Definición de "valor esperado neto de cuotas" tiene supuestos económicos** → Mitigación: encapsular la fórmula con sus supuestos explícitos y cubrir con test de monotonía (mejor estrategia ⇒ mayor valor), no con un número mágico.

## Open Questions

- Valor por defecto exacto del tamaño de bloque (¿10, 20, 25 días?): diferible; no cambia el contrato ni las tareas. Se fija al implementar, con default documentado y barrido posterior si hace falta.
- Malla de apalancamiento (rango y paso): diferible; se elige para que el óptimo interior sea visible en el reporte.
