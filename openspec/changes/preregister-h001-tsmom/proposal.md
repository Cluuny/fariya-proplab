## Why

El protocolo anti-autoengaño del documento maestro (§3.5) exige **pre-registrar** cada hipótesis —escribir su FALSADOR y su regla testeable— y committearlo **antes de correr nada** (§3.6, semana 6). Toda la capa técnica ya está lista y auditada (datos reales con calendario correcto, motor con swap y anualización por serie, `rolling_vol` gap-safe, guard de look-ahead, holdout escrito). H001 (Time-Series Momentum, Moskowitz-Ooi-Pedersen 2012) es la primera ficha: la más replicada de la literatura, opera en el horizonte correcto, usa sólo precios. Este change escribe la ficha para que el veredicto no se pueda mover cuando aparezca un resultado que guste.

## What Changes

- Se crea `hypotheses/H001_tsmom.yaml`: la ficha de pre-registro de H001 siguiendo el esquema §7.1 del documento maestro (fuente, clasificación, operabilidad, resultado original, evidencia externa, hipótesis testeable con FALSADOR, gestión de cola).
- Documenta las adaptaciones que nuestro setup impone sobre el paper: **9 instrumentos** (no 58 futuros), spot/CFD (no futuros), período **casi todo post-2010**, sizing a **8% de vol de portafolio** (§1.2), lookback en **meses de calendario** (no barras fijas), y el **swap sin dirección** (conservador para trend, bloqueante de H002).
- Declara la **exención de holdout** de H001 con su razón (replicación externa, período OOS respecto al paper, sin tuneo).

Fuera de alcance (change SEPARADO posterior): implementar la señal TSMOM en `signals.py`, correr el backtest y escribir el veredicto. Este change es SÓLO el pre-registro.

## Capabilities

### New Capabilities
<!-- Ninguna: es un artefacto de proyecto (ficha YAML), no una capability. skip_specs=true. -->

### Modified Capabilities
<!-- Ninguna. -->

## Impact

- **Artefacto nuevo**: `hypotheses/H001_tsmom.yaml`.
- **Sin cambios de código ni de spec.** No toca `src/` ni corre backtests.
- **Habilita** el siguiente change (implementación de TSMOM), que consumirá esta ficha como contrato: la señal debe implementar exactamente `regla_entrada`/`regla_salida`/`sizing`, y el veredicto se juzga contra el `FALSADOR` aquí escrito, sin editarlo.
- **Reglas duras respetadas**: falsador innegociable escrito antes del código; holdout declarado explícitamente.
