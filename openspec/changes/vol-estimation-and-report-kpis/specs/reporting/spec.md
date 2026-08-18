## ADDED Requirements

### Requirement: Los KPIs del reporte de avance se derivan del repo

Los indicadores cuantitativos del reporte de avance (número de tests, PRs, instrumentos, specs, changes, ventana de holdout, Sharpe de referencia) SHALL derivarse del repositorio mediante un comando, no teclearse a mano. El reporte de avance es el único artefacto mantenido a mano y por eso arrastra copy; sus KPIs SHALL provenir de una única fuente ejecutable (regla dura del README: todo reporte es regenerable con un comando).

#### Scenario: Un comando produce los KPIs del reporte
- **WHEN** se ejecuta el generador de KPIs (`scripts/report_kpis.py`)
- **THEN** emite, computados desde el repo, el número de tests, PRs mergeados, instrumentos activos, specs, changes archivados, la ventana de holdout y el Sharpe de referencia

#### Scenario: Los KPIs del reporte coinciden con el repo
- **WHEN** se comparan los KPIs mostrados en el reporte con la salida del generador
- **THEN** coinciden (no hay arrastre de copy tecleado a mano)
