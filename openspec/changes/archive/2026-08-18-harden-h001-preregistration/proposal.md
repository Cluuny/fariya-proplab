## Why

La ficha `hypotheses/H001_tsmom.yaml` ya está pre-registrada (change `preregister-h001-tsmom`), pero **antes de correr nada** (`estado: pre_registrado`, `intentos_realizados: 0`, `fecha_test: null`) el reviewer externo detectó seis huecos que la debilitan como pre-registro. Corregirlos ahora es legítimo —nada se ha ejecutado— y **fortalece** el contrato: una vez que se corra el backtest, el falsador se congela. Los seis:

1. **Una sola muestra agrupada, y el falsador descartaba su test más informativo.** `universo_test` describe una corrida agrupada con arranques escalonados; el falsador subsumía la cláusula "desaparece post-2010" alegando que la muestra es casi toda post-2010. Falso: FX+oro tienen 2003-2026 (~7 de 23 años pre-2010, ~22% de días-instrumento, y ese 22% contiene 2008 —el único régimen de estrés real que hay). Agrupado, no se sabría si un buen resultado vino de FX-2008 o de índices-2020, y no se puede ver la degradación post-2010 que reporta CXO (la afirmación más relevante de la evidencia externa).
2. **La zona 0.2–0.4 no tiene regla** y es donde el cálculo Grinold-Kahn dice que caerá el resultado. Un limbo es donde vive la tentación de probar variantes.
3. **No está escrita la dirección esperada de cada desviación vs el paper** ni el Sharpe central esperado. Sin expectativa comprometida, un 0.45 se lee como éxito y un 0.25 como "mi universo es distinto" —ambas lecturas post-hoc.
4. **No hay protocolo de sensibilidad al swap** (el swap es un placeholder; el veredicto no debe depender de él sin decirlo).
5. **El vol-targeting a 8% podría ser look-ahead** si se calcula sobre la vol realizada de toda la serie. Vive en la capa de señal → el guard de look-ahead del motor no lo atrapa.
6. **El día de rebalanceo y la política de alineación no están escritos.** El punto del pre-registro es que queden escritos aunque estén en código.

## What Changes

Se edita **sólo** `hypotheses/H001_tsmom.yaml` (sigue siendo `pre_registrado`, `intentos_realizados: 0`):

- **`universo_test` → dos muestras reportadas por separado:** Muestra A (FX+oro, 2004-2026, incluye 2008) y Muestra B (los 9, 2015-2026, todos con lookback completo).
- **Falsador: se devuelve la cláusula post-2010.** Regla de dos muestras: si A funciona y B no, **eso es el hallazgo** (degradación post-2010), no una molestia.
- **`zona_marginal`:** para Sharpe neto en [0.2, 0.4], un único chequeo de robustez pre-especificado (lookback de 6 meses), contado como intento (`n_intentos=2`), con deflated Sharpe reportado. Ninguna variante más.
- **`resultado_esperado`:** Sharpe central ~0.40, rango [0.25, 0.60], con la derivación Grinold-Kahn (IR ≈ IC·√BR) y la **dirección esperada de cada desviación** (9 vs 58 → baja; diario vs mensual → neutro en Sharpe, sube costos; CFD spot vs futuros → baja; 2004-2026 vs 1965-2009 → baja).
- **`sensibilidad_costos`:** swap en [0.0, 0.3, 1.0] bp/día, las tres reportadas; si el veredicto cambia de lado del falsador dentro del rango, se declara que el veredicto es sobre el placeholder.
- **`sizing`:** se especifica que el escalado a 8% de vol de portafolio es **ex-ante** (escalar rodante que en cada fecha usa sólo vol observada hasta ahí), no sobre la vol realizada de toda la serie.
- **`rebalanceo` + `alineacion`:** día de decisión determinista (primer día hábil del mes; si no cotiza, el siguiente día hábil del panel), y la política de alineación escrita (unión de fechas, ffill del precio por instrumento, retorno del cruce al día de reapertura).

Fuera de alcance: implementar la señal, correr backtests. Sigue siendo sólo la ficha.

## Capabilities

### New Capabilities
<!-- Ninguna: artefacto de proyecto (ficha YAML). skip_specs=true. -->

### Modified Capabilities
<!-- Ninguna. -->

## Impact

- **Artefacto editado**: `hypotheses/H001_tsmom.yaml` (sigue `pre_registrado`).
- **Sin cambios de código ni de spec.** No toca `src/` ni corre backtests.
- **Legítimo porque nada se ha ejecutado**: se documenta explícitamente en la ficha que la enmienda es pre-ejecución; tras el primer test el falsador se congela.
- **Fortalece** el contrato que consumirá el change de implementación de TSMOM.
