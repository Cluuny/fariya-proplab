## Context

Ver `proposal.md` — Why. El repositorio arranca prácticamente vacío (sólo el documento maestro y el scaffolding de OpenSpec). Este change materializa el Bloque A del cronograma (secciones 3.3, 3.4 y 8.2 del documento maestro). Restricción física clave: **este directorio (`fariya-proplab`) ya es la raíz que el documento llama `prop-lab`; no se crea ninguna subcarpeta `prop-lab/`** — la estructura va directo en la raíz. Herramientas ya presentes en la máquina: Python 3.14 y `uv`.

## Goals / Non-Goals

**Goals:**
- Estructura plana del repo tal cual la sección 3.3, en la raíz.
- Pipeline de datos que produzca parquets limpios validados + reporte de calidad (`data-pipeline`).
- Contrato de señal pura y una señal de referencia buy & hold (`signal-contract`).
- Motor de backtest con costos, verificable contra un Sharpe histórico conocido (`backtest-engine`).
- Reporte reproducible de un solo comando (`reporting`).
- Dejar los "ganchos" de fases futuras (`challenge.py` stub, `hypotheses/`, `notebooks/`, `results/`) sin implementar.

**Non-Goals:**
- Implementar el simulador de barreras / bootstrap (`challenge.py`) — Bloque B, change aparte.
- Escribir hipótesis reales H001–H005.
- Cualquier parte del Flujo 2 (agentes, arXiv, n8n, RAG).
- Automatizar la descarga de Dukascopy: la obtención de crudos es un paso previo manual; el pipeline opera sobre archivos locales en `data/raw/`.

## Decisions

### D1 — Construcción propia sobre `pandas`/`numpy`, no un framework de backtest
El documento (sección 6.4) descarta gs-quant, TradingAgents y Superalgos, y elige construcción propia: el backtest requerido es simple (barras diarias, ~20 instrumentos, rebalanceo semanal) y ninguna librería calcula `P(pasar)`. Stack: `pandas + numpy`, `polars` opcional si aparece un cuello de botella de velocidad. Gestión con `uv` (`pyproject.toml`). **Alternativa considerada:** vectorbt — descartada por ahora; el motor propio mantiene el contrato de funciones puras que necesita el Flujo 2.

### D2 — `data/raw/` inmutable; `data/clean/` derivado y regenerable
`loaders.py` sólo lee de `raw/` y escribe en `clean/`. Nunca sobrescribe crudos. Esto da reproducibilidad y permite re-generar `clean/` ante un cambio en las reglas de validación. **Alternativa:** limpiar in-place — descartada, rompe auditabilidad.

### D3 — `signals.py` = funciones puras `(prices, ...) -> pesos`
Sin estado, sin I/O, `sum(|pesos|) <= 1`. Es el contrato con el futuro Flujo 2 y lo que hace cada estrategia testeable en aislamiento (~20 líneas). Se define como un `Protocol`/typing + un validador de invariante reutilizable. **Alternativa:** clases de estrategia con estado — descartada, contradice el documento y complica la generación de código por agentes.

### D4 — `engine.py` es el único punto de costos
Comisión, spread, slippage e impacto se aplican exclusivamente aquí. Los pesos objetivo entran "limpios" desde `signals.py`. Verificación de corrección: buy & hold de un índice debe reproducir su Sharpe histórico conocido dentro de tolerancia. **Alternativa:** costos repartidos entre módulos — descartada, el documento lo prohíbe explícitamente ("único componente que toca costos").

### D5 — `report.py` regenera todo con un comando
Equity curve, Sharpe, max DD, distribución. Salida HTML/markdown determinista. Los artefactos de reporte por hipótesis vivirán en `results/` (un directorio por hipótesis, inmutable) en fases futuras; en este change basta generar el reporte de una estrategia de referencia. **Alternativa:** notebook manual — descartada, no reproducible.

### D6 — Parámetros de costo y tolerancia de Sharpe como configuración explícita
Los costos por instrumento (comisión, spread típico) y la tolerancia con la que buy & hold debe reproducir el Sharpe histórico se declaran en configuración/constantes explícitas y versionadas, no incrustados ad hoc, para que el test de verificación sea reproducible y ajustable.

## Risks / Trade-offs

- **Datos de Dukascopy ≠ feed de la prop firm** → el documento ya lo marca; la mitigación (medir factor de degradación contra feed real) es Semana 11, fuera de este change. Aquí sólo se documenta el supuesto.
- **Reproducir "el Sharpe histórico conocido" depende de la fuente del número de referencia** → mitigación: fijar la fuente y la ventana del Sharpe de referencia en configuración (D6) y expresar la aceptación como una tolerancia, no una igualdad exacta.
- **Detección de saltos por cambio de contrato en índices/futuros puede tener falsos positivos** → mitigación: el reporte de calidad los lista para revisión humana ("mirarlas con los ojos", sección 8.2) en vez de corregir automáticamente.
- **Python 3.14 es reciente; alguna dependencia podría no tener wheels** → mitigación: `uv` fija versiones; si `polars` da problemas, es opcional y se difiere.

## Open Questions

- Formato exacto del reporte de calidad (¿markdown vs HTML vs consola?): diferible; no cambia specs ni tareas. Se decidirá al implementar `loaders.py`, por defecto markdown legible.
- Convención de nombres de los archivos crudos de Dukascopy: se ajustará al inspeccionar el primer dump real; no afecta el contrato de `loaders.py`.
