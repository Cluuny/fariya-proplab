# data-pipeline Specification

## Purpose

La capa de datos convierte dumps crudos de un proveedor externo en series de precios limpias, validadas y reproducibles, con un reporte de calidad por instrumento, de modo que ninguna estrategia posterior opere sobre datos silenciosamente rotos.

## Requirements

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

### Requirement: Sesiones de trading (sin barras de fin de semana)

El sistema SHALL conservar en la serie limpia únicamente barras de días de trading (Lun-Vie), descartando las barras de sábado y domingo. Las barras de fin de semana de Dukascopy son sesiones parciales (pocas horas) que inflan el conteo de barras y deflactan la volatilidad estimada; una barra diaria debe representar una sesión completa.

#### Scenario: La serie limpia no contiene barras de fin de semana
- **WHEN** se limpia una serie de Dukascopy que incluye barras de sábado o domingo
- **THEN** la serie limpia resultante no contiene barras con día de la semana sábado ni domingo

#### Scenario: El conteo de barras por año es coherente con días hábiles
- **WHEN** se inspecciona una serie de FX limpia de varios años
- **THEN** el número de barras por año se aproxima al de días hábiles (~252-261), no a ~313 (que incluía la barra de domingo)

### Requirement: Validación de calidad de datos

El sistema SHALL validar cada serie y detectar, como mínimo: gaps en el calendario de trading, precios en cero o no positivos, fechas duplicadas, retornos anómalos (magnitud mayor a 5σ), feriados mal marcados y gaps de sesión abruptos. Cada anomalía detectada SHALL quedar registrada con instrumento, fecha y tipo. Los gaps de sesión SHALL registrarse bajo el tipo `session_gap` (un **gap de apertura** entre sesiones, `open` vs cierre previo, distinto del retorno close-to-close), NO como `contract_jump`: sobre spot FX no hay contratos, y el nombre debe reflejar que se detecta un gap de sesión, no un cambio de contrato. Un mismo evento NO SHALL contarse dos veces bajo dos tipos.

#### Scenario: Se detectan y reportan anomalías
- **WHEN** una serie contiene un retorno de magnitud mayor a 5σ, un precio en cero o una fecha duplicada
- **THEN** el sistema registra cada caso con instrumento, fecha y tipo de anomalía en el reporte de calidad

#### Scenario: Serie sin anomalías pasa limpia
- **WHEN** una serie no contiene ninguna de las anomalías validadas
- **THEN** el reporte de calidad marca ese instrumento como sin anomalías detectadas

#### Scenario: Salto de contrato y retorno anómalo son señales distintas
- **WHEN** una serie tiene un gap de apertura grande entre sesiones sin un retorno close-to-close anómalo (o viceversa)
- **THEN** el gap se registra como `session_gap` y el retorno anómalo como `anomalous_return`, sin que un mismo evento se cuente bajo ambos tipos

### Requirement: Reporte de calidad legible

El sistema SHALL producir un reporte de calidad legible por humano que resuma, por instrumento: rango de fechas cubierto, número de observaciones, días faltantes, y el conteo de cada tipo de anomalía detectada.

#### Scenario: Un comando produce parquets y reporte
- **WHEN** el operador ejecuta el comando de ingesta (`python -m src.loaders`)
- **THEN** el comando termina sin error, produce los parquets limpios y emite un reporte de calidad legible que cubre cada instrumento procesado
