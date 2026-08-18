## Purpose

La capa de datos convierte dumps crudos de un proveedor externo en series de precios limpias, validadas y reproducibles, con un reporte de calidad por instrumento, de modo que ninguna estrategia posterior opere sobre datos silenciosamente rotos.

## ADDED Requirements

### Requirement: Ingesta inmutable de datos crudos

El sistema SHALL tratar los datos crudos como inmutables: nunca modifica, sobrescribe ni borra archivos en `data/raw/`. Toda salida limpia es derivada y regenerable a partir de los crudos.

#### Scenario: El pipeline no altera los crudos
- **WHEN** se ejecuta el pipeline de limpieza sobre `data/raw/`
- **THEN** los archivos de `data/raw/` permanecen idénticos (mismo contenido y hash) tras la ejecución

#### Scenario: Regeneración determinista de datos limpios
- **WHEN** se ejecuta el pipeline dos veces sobre los mismos crudos
- **THEN** los parquets producidos en `data/clean/` son idénticos entre ejecuciones

### Requirement: Conversión a parquet limpio por instrumento

El sistema SHALL producir exactamente un archivo parquet limpio por instrumento en `data/clean/`, con una serie temporal diaria (EOD) indexada por fecha y columnas de precio (al menos OHLC o cierre) ordenadas cronológicamente y sin fechas duplicadas.

#### Scenario: Un parquet por instrumento
- **WHEN** el pipeline procesa N instrumentos con datos crudos disponibles
- **THEN** produce N archivos parquet en `data/clean/`, uno por instrumento, cada uno indexado por fecha ascendente y sin duplicados de fecha

### Requirement: Validación de calidad de datos

El sistema SHALL validar cada serie y detectar, como mínimo: gaps en el calendario de trading, precios en cero o no positivos, fechas duplicadas, retornos anómalos (magnitud mayor a 5σ), feriados mal marcados y saltos abruptos atribuibles a cambio de contrato. Cada anomalía detectada SHALL quedar registrada con instrumento, fecha y tipo.

#### Scenario: Se detectan y reportan anomalías
- **WHEN** una serie contiene un retorno de magnitud mayor a 5σ, un precio en cero o una fecha duplicada
- **THEN** el sistema registra cada caso con instrumento, fecha y tipo de anomalía en el reporte de calidad

#### Scenario: Serie sin anomalías pasa limpia
- **WHEN** una serie no contiene ninguna de las anomalías validadas
- **THEN** el reporte de calidad marca ese instrumento como sin anomalías detectadas

### Requirement: Reporte de calidad legible

El sistema SHALL producir un reporte de calidad legible por humano que resuma, por instrumento: rango de fechas cubierto, número de observaciones, días faltantes, y el conteo de cada tipo de anomalía detectada.

#### Scenario: Un comando produce parquets y reporte
- **WHEN** el operador ejecuta el comando de ingesta (`python -m src.loaders`)
- **THEN** el comando termina sin error, produce los parquets limpios y emite un reporte de calidad legible que cubre cada instrumento procesado
