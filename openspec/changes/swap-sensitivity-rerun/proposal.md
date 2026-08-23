## Why

Con el swap corregido (direccional histórico), re-correr H001 y H007 como DIAGNÓSTICO de sensibilidad para responder una pregunta de fondo: ¿cuántas de las tres falsaciones fueron sobre la ESTRATEGIA y cuántas sobre el PLACEHOLDER de swap?

## Regla crítica

Esto **NO son nuevos intentos y NO cambia los veredictos registrados**. H001 y H007 quedan **MUERTAS**; sus fichas están congeladas; `intentos_familia_trend` NO se incrementa. El entregable es un documento aparte: `docs/swap_sensitivity.md`.

## What Changes

- **`scripts/swap_sensitivity.py`** (nuevo) + **`docs/swap_sensitivity.md`** (entregable): tabla para H001 (A,B) y H007 (A,B) del Sharpe neto bajo (1) unsigned 0.3 bp/d — el que dictó los veredictos —, (2) direccional histórico MULT 1.0, (3) direccional histórico MULT 1.5, con el veredicto que daría cada columna. Y la métrica clave **E[carry·w] anualizado** por muestra.
- **Expectativa comprometida, escrita ANTES de correr** en el documento: E[carry·w] ≈ 0 y las falsaciones se sostienen o empeoran.

## Resultado (confirma la expectativa)

| Muestra | unsigned 0.3 | direccional MULT 1.0 | MULT 1.5 | E[carry·w] |
|---|---|---|---|---|
| H001-A | 0.078 | 0.028 | −0.083 | +0.19%/año |
| H001-B | 0.135 | 0.080 | −0.034 | +0.14%/año |
| H007-A | 0.184 | 0.155 | 0.032 | +0.42%/año |
| H007-B | 0.040 | −0.008 | −0.132 | +0.25%/año |

**Todas muertas en todas las columnas.** E[carry·w] ≈ 0 → trend y carry NO se alinean (el signo de la posición lo dicta la tendencia, no el diferencial). El modelo corregido es MÁS punitivo (margen 0.42 > 0.30), no menos.

**Las tres falsaciones eran REALES, sobre la estrategia, no sobre el placeholder de swap.** La hipótesis de que "el swap estaba matando cosas injustamente" queda refutada con datos. Es información valiosa: cierra la duda de si el parámetro de costo sesgó los veredictos — no lo hizo.

## Capabilities

### New/Modified Capabilities
<!-- Ninguna: diagnóstico + documento. No toca fichas ni veredictos. skip_specs=true. -->

## Impact

- **Código**: `scripts/swap_sensitivity.py` (nuevo, reusa el motor con carry_matrix). **Artefacto**: `docs/swap_sensitivity.md`.
- **Sin cambios a fichas, veredictos ni intentos.** H001/H007 siguen muertas.
