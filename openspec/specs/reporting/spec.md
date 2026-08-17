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
