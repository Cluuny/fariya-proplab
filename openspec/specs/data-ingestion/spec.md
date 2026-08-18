# data-ingestion Specification

## Purpose

La capa de ingesta automatiza la obtención de barras diarias EOD desde el feed público de Dukascopy hacia `data/raw/`, con un mapeo explícito de símbolos internos a los de Dukascopy, para que el pipeline de datos deje de depender de una descarga manual y opere sobre datos reales reproducibles.

## Requirements

### Requirement: Descarga de barras diarias por instrumento

El sistema SHALL descargar barras diarias EOD (fecha + OHLC) desde el feed público de Dukascopy para cada instrumento del universo configurado, cubriendo un rango de fechas dado, y escribirlas en `data/raw/` en el formato que la capa de datos (`loaders`) consume.

#### Scenario: Un comando llena data/raw/
- **WHEN** el operador ejecuta el comando de ingesta para el universo configurado y un rango de fechas
- **THEN** produce un archivo por instrumento en `data/raw/` con barras diarias (fecha + OHLC) en el formato que `loaders` acepta

#### Scenario: La ingesta es idempotente
- **WHEN** el comando de ingesta se ejecuta dos veces con el mismo universo y rango
- **THEN** el contenido descargado para cada instrumento es el mismo (no duplica ni corrompe archivos existentes)

### Requirement: Mapeo explícito de símbolos internos a Dukascopy

El sistema SHALL mantener un mapeo explícito y versionado de cada símbolo interno (p. ej. `SPX500`) al símbolo correspondiente de Dukascopy (p. ej. `USA500IDXUSD`). El sistema SHALL fallar de forma visible si un instrumento del universo no tiene mapeo, en vez de descargar datos equivocados o silenciosamente vacíos.

#### Scenario: Cada instrumento del universo tiene mapeo
- **WHEN** se valida la configuración de ingesta contra el universo
- **THEN** todo instrumento del universo tiene un símbolo de Dukascopy asociado

#### Scenario: Un símbolo sin mapeo es un error visible
- **WHEN** se intenta ingerir un instrumento sin entrada en el mapeo
- **THEN** el sistema falla con un error explícito que nombra el instrumento, sin producir un archivo vacío o incorrecto

### Requirement: Universo decorrelacionado

El sistema SHALL configurar un universo de instrumentos que incluya diversificación por clase y geografía (no solo índices de renta variable altamente correlacionados), de modo que el portafolio pueda bajar volatilidad por decorrelación. En particular, el universo SHALL incluir energía (p. ej. Brent) y Asia (p. ej. Nikkei) en lugar de índices redundantes.

#### Scenario: El universo no es solo índices equity correlacionados
- **WHEN** se inspecciona el universo configurado
- **THEN** incluye instrumentos de energía y de Asia, y no consiste únicamente en índices de renta variable altamente correlacionados

### Requirement: Robustez de red y datos crudos inmutables

El sistema SHALL manejar fallos de red con reintentos acotados y rate-limiting, y SHALL escribir en `data/raw/` de forma que los archivos crudos permanezcan inmutables para la capa de datos (que sigue derivando `clean/` de ellos). El sistema SHALL NOT dejar archivos crudos parcialmente escritos ante un fallo.

#### Scenario: Un fallo de red no deja crudos corruptos
- **WHEN** una descarga falla a mitad de camino tras agotar los reintentos
- **THEN** no queda un archivo crudo parcial/corrupto para ese instrumento; el fallo se reporta

#### Scenario: Los crudos descargados pasan la validación de calidad
- **WHEN** se corre `loaders` sobre los crudos descargados
- **THEN** el pipeline los procesa y su reporte de calidad marca las anomalías reales (gaps, feriados, saltos por rollover) sin romperse
