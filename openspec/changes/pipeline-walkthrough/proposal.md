# Explicación punta a punta del pipeline de investigación

## Why

El pipeline está construido, corrido (91 candidatos) y cerrado, pero no hay un documento en prosa
que permita al operador entenderlo COMPLETO sin leer el código, y —lo más importante— saber
DÓNDE no puede confiar en él. Hace falta para poder delegarle la búsqueda con los ojos abiertos.

## What Changes

**`docs/pipeline_walkthrough.md`** (sólo documentación), escrito para quien va a DELEGAR la búsqueda:
- Diagrama de flujo en texto con los conteos REALES de las runs 001-002 en cada estación.
- (1) El recorrido de TRES candidatos reales, uno por tipo de muerte (E2, E2.5, cribado
  aritmético), con el abstract real en cada paso.
- (2) Descubrimiento (E1): cada fuente, la consulta literal, cadencia, densidad medida y el mapa de
  puntos ciegos (cómo entra una fuente que menciona el operador).
- (3) Los filtros (E2, E2.5, E3) con la regla literal, el % que mató, y los falsos positivos/negativos
  conocidos (los 3 bugs de subcadena, los 4 falsos positivos del eje, el falso rechazo de
  «Is Trend Still Your Friend?» por 'fundamental').
- (4) Extracción (E4): el seam NO cableado, la validación anti-alucinación implementada, el esquema.
- (5) Adversario (E5): los 11 ejes con texto literal, cuáles son críticos, de dónde salió cada uno
  (5 de errores propios), `hallazgo_no_enumerado`, y la limitación (test ciego AQR = NO DETECTADO).
- (6) «Dónde puede engañarme el pipeline» — los modos de fallo conocidos y qué NO garantiza pasar
  todas las estaciones.
- (7) Cómo correrlo: comandos, determinista vs sesión, throughput, estado, contador de parada.

Todo con citas `archivo:línea` para que sea verificable contra el código.

## Impact

- NUEVO: `docs/pipeline_walkthrough.md`. Sin cambios de código, sin tests, holdout intacto.
