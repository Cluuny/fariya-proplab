## Context

Ver `proposal.md`. Este change edita un único artefacto de texto (`hypotheses/H001_tsmom.yaml`) para cerrar seis huecos que el reviewer marcó **antes de correr nada**. No hay código ni spec. La decisión de la zona marginal ya se tomó con el usuario (un chequeo de robustez, no parked).

## Goals / Non-Goals

**Goals:** un pre-registro que (a) separe la muestra pre-2010 para poder ver la degradación, (b) tenga una regla escrita para todo rango de Sharpe incluido el limbo, (c) comprometa una expectativa numérica derivada, (d) declare la sensibilidad al swap, (e) cierre el look-ahead del sizing, (f) fije la mecánica de rebalanceo/alineación.

**Non-Goals:** implementar TSMOM, correr backtests. No editar el falsador **después** del primer test (aquí se edita antes, con `intentos_realizados: 0`).

## Decisions (contenido de la ficha)

### D1 — Dos muestras, no una agrupada
`universo_test` pasa a dos bloques reportados por separado:
- **Muestra A**: FX + oro (6 instrumentos), 2004-2026. Incluye 2008 (~22% de días-instrumento son pre-2010). Es el test de estrés.
- **Muestra B**: los 9, 2015-2026. Todos con 12 meses de lookback completo (GER40 arranca 2013-09-30 → tradeable desde ~2014-10; se toma 2015 para holgura).

Razón estructural: agrupado no se puede atribuir un buen resultado a un régimen, ni ver la degradación post-2010 que CXO reporta.

### D2 — El falsador recupera la cláusula post-2010, como regla de dos muestras
El falsador de nivel (Sharpe neto < 0.2 → muerta) se evalúa **por muestra**. Se añade la regla de contraste: **si A funciona (Sharpe ≥ 0.4) y B no (< 0.2), el hallazgo es la degradación post-2010** —H001 no se declara viable en régimen moderno, y se documenta como efecto degradado, no como "molestia". Esto devuelve el test más informativo que la subsunción había borrado.

### D3 — Zona marginal [0.2, 0.4]: un chequeo de robustez (decisión del usuario)
`zona_marginal.decision: un_chequeo_robustez`. Regla: se corre **una sola** variante pre-especificada —lookback de 6 meses en vez de 12— contada como intento (`intentos_realizados` pasaría a 2), y se reporta el **deflated Sharpe** (corrección por multiplicidad). Ninguna variante más. Cierra el limbo donde vive el fishing.

### D4 — `resultado_esperado` con derivación Grinold-Kahn
Campo nuevo. Sharpe central ~0.40, rango [0.25, 0.60]. Derivación: IR ≈ IC·√BR; 1.2 × √(9/58) = 0.47 naive; amplitud efectiva < 9 (factor USD compartido por 5 pares; índices correlacionados 0.5-0.7 → ~4-5 apuestas independientes); degradación post-2010 resta → central ~0.35-0.45. Y la **dirección esperada por desviación**: 9 vs 58 → BAJA (dominante); diario vs mensual → NEUTRO en Sharpe, SUBE turnover/costos; CFD spot vs futuros → BAJA (swap peor, sin roll yield); 2004-2026 vs 1965-2009 → BAJA (degradación). Convierte el test en calibración: compromete la expectativa para que 0.45 no se lea como éxito post-hoc.

### D5 — `sensibilidad_costos`: tres corridas de swap
`swap_bp_dia: [0.0, 0.3, 1.0]`, las tres reportadas. Si el veredicto cruza el falsador dentro del rango, el veredicto es sobre el **placeholder** de swap, no sobre la estrategia, y se declara así.

### D6 — Vol-targeting ex-ante (cierra look-ahead de la capa de señal)
`sizing` se precisa: el escalado global a ~8% de vol de portafolio SHALL ser un **escalar rodante** que en cada fecha use sólo vol observada hasta esa fecha (p. ej. vol de portafolio a 63 días con `w.shift(1)`), NO la vol realizada de toda la serie. Nota: no afecta al falsador (Sharpe invariante al escalado) pero un backtest con look-ahead en el sizing es un backtest sucio y contamina el diagnóstico del simulador.

### D7 — Rebalanceo y alineación deterministas, escritos
- `rebalanceo.dia`: primer día hábil del mes; si un instrumento no cotiza ese día, su decisión usa el precio disponible más reciente (ya ffill) y la ejecución cae en su siguiente día de cotización vía el `shift(1)` del motor.
- `alineacion`: unión de fechas del panel; ffill del precio por instrumento; el retorno que cruza un hueco se atribuye al día de reapertura (coincide con `engine._asset_returns`). Se escribe aunque esté en código: el pre-registro exige que quede fijado.

## Risks / Trade-offs

- **Editar un pre-registro puede leerse como mover el poste.** Mitigación: se hace con `intentos_realizados: 0` / `fecha_test: null` y se documenta en la ficha que la enmienda es pre-ejecución. Tras el primer test, congelado.
- **Muestra A tiene 6 instrumentos, menos amplitud** → su Sharpe esperado es aún más bajo que el del panel completo; se interpreta con esa lente, no contra el 1.2 del paper.

## Open Questions

- Ninguna que bloquee. Los umbrales exactos del deflated Sharpe y la construcción del escalar rodante se fijan en el change de implementación, consistentes con lo aquí escrito.
