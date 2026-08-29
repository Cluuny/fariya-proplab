# README orientado a un agente (fundamentos del código)

## Why

El README anterior era un resumen de cierre de diez líneas. El operador pide un README que permita a
un agente (como Claude) entender el sistema de forma QUIRÚRGICA desde los fundamentos del código: el
modelo mental, el flujo de datos, los contratos entre módulos y las invariantes, con anclas
`archivo:símbolo` para razonar o modificar sin abrir cada archivo.

## What Changes

Reescribe `README.md` como un mapa del código orientado a un agente:
- Nota inicial dirigida a un agente + puntero a `docs/RECAP.md` para la narrativa auditada.
- El modelo mental: los DOS flujos (backtest de hipótesis conocida vs pipeline de investigación) con
  diagrama de flujo de datos.
- Los TRES contratos duros (raw inmutable, señales puras `prices→weights` con `sum(|w|)≤max_gross` y
  sin look-ahead, engine único punto de coste) + dos invariantes (holdout sagrado, sin knobs ocultos).
- Mapa de módulos `src/` (tabla: responsabilidad + símbolos públicos clave), `src/pipeline/` (las 7
  estaciones + soporte) y `src/crypto/` (bloques 1–4), con anclas verificadas contra el código.
- Cómo correrlo (uv, tests, los scripts de las mediciones del veredicto), dónde vive el estado.
- Dónde vive el análisis (`docs/`), y las convenciones para cambiar el repo (OpenSpec-por-cambio,
  rama, contratos, fichas congeladas, sin knobs ocultos).

## Impact

- MOD: `README.md` (reescritura orientada a agente). Sin cambios de código; holdout intacto.
