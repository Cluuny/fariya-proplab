# reporting Specification

## Purpose

La capa de reporte regenera, desde un solo comando y de forma totalmente reproducible, el resumen de desempeño de una estrategia, para que cada veredicto sea auditable y comparable sin ejecución manual.

## Requirements

### Requirement: Generación de reporte de desempeño

El sistema SHALL generar, a partir de una serie de retornos netos, un reporte que incluya como mínimo: equity curve, Sharpe, max drawdown y distribución de retornos. El reporte SHALL emitirse en un formato legible (HTML o markdown).

#### Scenario: El reporte contiene las métricas mínimas
- **WHEN** se genera el reporte a partir de una serie de retornos netos
- **THEN** el reporte incluye equity curve, Sharpe, max drawdown y distribución de retornos

### Requirement: Reproducibilidad total con un comando

El sistema SHALL permitir regenerar el reporte completo con un único comando, de forma determinista: mismas entradas producen el mismo reporte.

#### Scenario: Un comando regenera el reporte
- **WHEN** el operador ejecuta el comando de reporte sobre una estrategia dada
- **THEN** el comando produce el archivo de reporte sin pasos manuales adicionales

#### Scenario: Reporte determinista
- **WHEN** se genera el reporte dos veces sobre las mismas entradas
- **THEN** ambos reportes contienen las mismas métricas con los mismos valores

### Requirement: Los KPIs del reporte de avance se derivan del repo

Los indicadores cuantitativos del reporte de avance (número de tests, PRs, instrumentos, specs, changes, ventana de holdout, Sharpe de referencia) SHALL derivarse del repositorio mediante un comando, no teclearse a mano. El reporte de avance es el único artefacto mantenido a mano y por eso arrastra copy; sus KPIs SHALL provenir de una única fuente ejecutable (regla dura del README: todo reporte es regenerable con un comando).

#### Scenario: Un comando produce los KPIs del reporte
- **WHEN** se ejecuta el generador de KPIs (`scripts/report_kpis.py`)
- **THEN** emite, computados desde el repo, el número de tests, PRs mergeados, instrumentos activos, specs, changes archivados, la ventana de holdout y el Sharpe de referencia

#### Scenario: Los KPIs del reporte coinciden con el repo
- **WHEN** se comparan los KPIs mostrados en el reporte con la salida del generador
- **THEN** coinciden (no hay arrastre de copy tecleado a mano)
