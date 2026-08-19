## Why

Revisión del reporte de H001 detectó cuatro cosas antes de archivar:

1. **Una conclusión no soportada.** El reporte dice "regla de dos muestras: NO activa degradación post-2010 (B ≥ A)". La comparación está confundida: A (FX+oro, 2004-2026) y B (los 9, 2015-2026) difieren en **universo Y período** a la vez, así que no se puede atribuir la diferencia al régimen temporal. Donde SÍ se aísla el tiempo (universo constante) es **dentro de la Muestra A**, y su equity muestra degradación clara. Verificado: A 2004-2016 Sharpe +0.287 (+30%), A 2016-2026 Sharpe −0.178 (−17.8%). El agregado 0.078 la escondía.
2. **Falta el diagnóstico de turnover.** El swap 0.0 NO es "sin costos" (sigue cobrando spread/slippage sobre rotación), así que no distinguía "efecto débil" de "rotación se lo come". Verificado: turnover ~9×/año (≈mensual, como el diseño; el ffill mensual sí sostiene los pesos) y `sharpe_zero_cost` (A +0.244, B +0.308) apenas supera al swap-0.0 → **es la historia del efecto débil, no la del turnover**. Es calibración del motor que arrastramos a TODAS las hipótesis: si el turnover fuera 60× cuando el diseño implica ~12×, mataríamos hipótesis futuras por la razón equivocada.
3. **H005 quedó subsumida.** La cola tiene H005 = "trend con vol targeting", pero la implementación de H001 ya usa vol-inversa + vol targeting de portafolio. Es la misma hipótesis → duplicada, se cierra.
4. **H001 lista para archivar** con `estado: muerta`.

## What Changes

- **`scripts/run_h001.py`**: (a) corrige la interpretación —la comparación A vs B no evalúa régimen (confusión universo+período); la degradación se muestra **intra-muestra en A** con el split 2004-2016 vs 2016-2026; (b) añade y reporta **`sharpe_zero_cost`** (`apply_costs=False`) y **`turnover_anual`** (`sum|Δw|/año`) por muestra; (c) añade una nota de que el max DD relativo a la vol (−30.8% con 8.8% vol) habría matado H001 igual → el falsador de Sharpe es necesario pero no suficiente; max DD/vol como diagnóstico de primera línea para futuras hipótesis.
- **`hypotheses/QUEUE.md`** (nuevo): cola de hipótesis con H001 = muerta (archivada) y **H005 = duplicada de H001, cerrada**.
- **Archiva la ficha**: `hypotheses/H001_tsmom.yaml` → `hypotheses/archive/H001_tsmom.yaml` (`estado: muerta`, ya congelado).

Fuera de alcance: revivir H001 (muerta), nuevas hipótesis.

## Capabilities

### New/Modified Capabilities
<!-- Ninguna: correcciones de reporte + artefactos de proyecto. skip_specs=true. -->

## Impact

- **Código**: `scripts/run_h001.py` (dos diagnósticos nuevos + interpretación corregida).
- **Artefactos**: `hypotheses/QUEUE.md` (nuevo), `hypotheses/H001_tsmom.yaml` → `hypotheses/archive/`.
- **Sin cambio de veredicto** (sigue muerta); se corrige el registro y se añade calibración reutilizable.
