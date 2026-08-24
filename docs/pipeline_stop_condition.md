# Condición de parada del pipeline de investigación

Escrita ANTES de construir el pipeline completo, para que no se reinterprete después.

## El motivo del pipeline

Siete de las ocho familias con veredicto salieron del reviewer; cinco de siete fueron
precio puro; nunca se leyó un paper completo. Esa dependencia de una sola fuente de ideas es
un fallo del programa, tan real como el suelo de costes. **El pipeline existe para romper esa
dependencia, y se juzga por si produce supervivientes que el reviewer NO habría propuesto.**

## La condición de parada (textual)

> "Si tras procesar 200 candidatos ninguno pasa el filtro #6 con un bruto respaldado por
> literatura, el diagnóstico NO es 'faltan fuentes' sino 'las restricciones son de acceso a
> datos y vehículo, no de ideas' — y eso ya está establecido en `docs/program_verdict.md`.
> En ese caso el pipeline se declara concluido y no se amplían fuentes buscando el
> candidato 201."

## Parámetros (decididos por el operador)

- `presupuesto_datos` = **125 USD/mes** (≈ 500.000 COP)
- `N_condicion_parada` = **200 candidatos procesados**
- `alcance` = pipeline completo (estaciones 1-7)

## Contador

El reporte del pipeline (`python -m scripts.pipeline report`) muestra un contador visible
**candidatos procesados / 200**. "Procesado" = un candidato que atravesó al menos el triaje
(estado distinto de `candidato`). El backfill de las 11 hipótesis conocidas cuenta como
procesadas (tienen veredicto).

## Qué NO es

No es una promesa de que el candidato 200 exista. Es un límite duro contra el sesgo de
"una fuente más": si 200 candidatos de fuentes académicas y no académicas no producen un
superviviente, la conclusión es la misma que ya tiene el programa —el cuello de botella es
de datos y vehículo, no de ideas— y se para.
