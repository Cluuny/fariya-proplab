## MODIFIED Requirements

### Requirement: Validación de calidad de datos

El sistema SHALL validar cada serie y detectar, como mínimo: gaps en el calendario de trading, precios en cero o no positivos, fechas duplicadas, retornos anómalos (magnitud mayor a 5σ), feriados mal marcados y saltos abruptos atribuibles a cambio de contrato. Cada anomalía detectada SHALL quedar registrada con instrumento, fecha y tipo. Los saltos por cambio de contrato SHALL detectarse como una señal **distinta** de los retornos anómalos —un **gap de apertura** entre sesiones (`open` vs cierre previo), no el retorno close-to-close— de modo que un mismo evento NO se cuente dos veces bajo dos tipos.

#### Scenario: Se detectan y reportan anomalías
- **WHEN** una serie contiene un retorno de magnitud mayor a 5σ, un precio en cero o una fecha duplicada
- **THEN** el sistema registra cada caso con instrumento, fecha y tipo de anomalía en el reporte de calidad

#### Scenario: Serie sin anomalías pasa limpia
- **WHEN** una serie no contiene ninguna de las anomalías validadas
- **THEN** el reporte de calidad marca ese instrumento como sin anomalías detectadas

#### Scenario: Salto de contrato y retorno anómalo son señales distintas
- **WHEN** una serie tiene un gap de apertura grande entre sesiones sin un retorno close-to-close anómalo (o viceversa)
- **THEN** el gap se registra como `contract_jump` y el retorno anómalo como `anomalous_return`, sin que un mismo evento se cuente bajo ambos tipos
