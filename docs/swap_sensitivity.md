# Sensibilidad al swap — diagnóstico retroactivo (Bloque 3)

**Esto NO cambia los veredictos.** H001 y H007 quedan **MUERTAS**; sus fichas están congeladas; `intentos_familia_trend` NO se incrementa. Es un diagnóstico para responder: ¿cuántas falsaciones fueron sobre la estrategia y cuántas sobre el placeholder de swap?

## Expectativa COMPROMETIDA (escrita ANTES de correr)

Se espera **E[carry·w] ≈ 0** y que las falsaciones **SE SOSTENGAN O EMPEOREN**. La
hipótesis previa de que "el swap estaba matando cosas injustamente" parece
equivocada: el carry se compensa contra la POSICIÓN, no reduce el margen, y en trend
el signo de la posición lo dicta la tendencia, NO el carry. Además el margen
corregido subió a 0.42 bp/d (factor 365/261), MÁS punitivo que el placeholder 0.30.

## Resultado — Sharpe neto por muestra y modelo de swap

| Muestra | unsigned 0.3 (dictó veredicto) | direccional hist. MULT 1.0 | direccional hist. MULT 1.5 |
|---|---|---|---|
| H001-A | +0.078 (muerta) | +0.028 (muerta) | -0.083 (muerta) |
| H001-B | +0.135 (muerta) | +0.080 (muerta) | -0.034 (muerta) |
| H007-A | +0.184 (muerta) | +0.155 (muerta) | +0.032 (muerta) |
| H007-B | +0.040 (muerta) | -0.008 (muerta) | -0.132 (muerta) |

## Métrica clave — E[carry·w] anualizado (¿se alinean trend y carry?)

| Muestra | E[carry·w] anual | lectura |
|---|---|---|
| H001-A | +0.19%/año | carry ≈ 0 (no se alinea) |
| H001-B | +0.14%/año | carry ≈ 0 (no se alinea) |
| H007-A | +0.42%/año | carry ≈ 0 (no se alinea) |
| H007-B | +0.25%/año | carry ≈ 0 (no se alinea) |

## Conclusión

- **E[carry·w] es pequeño en todas las muestras** (|máx| = 0.42%/año): trend y carry **no se alinean** — el signo de la posición lo dicta la tendencia, no el diferencial de tasas. El carry se compensa contra la posición, no reduce el margen.
- **El modelo corregido NO rescata nada**: bajo el swap direccional histórico (MULT 1.0) los veredictos son idénticos (todas muertas), y con MULT 1.5 empeoran (margen 0.42→0.63 bp/d). El margen corregido (0.42) es MÁS punitivo que el placeholder (0.30) que dictó los veredictos.

**Respuesta a la pregunta de fondo: las tres falsaciones eran REALES, sobre la estrategia, no sobre el placeholder de swap.** La hipótesis de que 'el swap estaba matando cosas injustamente' queda refutada con datos: el carry no compensa (trend no lo cosecha) y el margen real es mayor, no menor. Esto confirma la expectativa comprometida. Es información valiosa: cierra la duda sobre si el parámetro de costo sesgó los veredictos — no lo hizo.