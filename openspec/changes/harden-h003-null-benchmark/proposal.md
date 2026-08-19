## Why

La ficha de H003 se pre-registró, pero **antes de correr nada** (`intentos_realizados: 0`, `fecha_test: null`) el reviewer detectó tres fallas que la invalidan como diseño. Corregirlas ahora es legítimo —nada se ha ejecutado— y es obligatorio: el diseño actual **no puede falsarse**.

1. **El falsador no distingue la hipótesis del azar.** Estando long-only ~19% del tiempo en índices durante el bull market 2011-2023, una estrategia NULA (larga 4 días ALEATORIOS/mes) ya produce un Sharpe alto solo por beta + tiempo en mercado. Verificado con datos reales: el nulo (random 4d/mes, 3 índices) tiene **Sharpe medio ≈ 0.24 y p95 ≈ 0.65**. Mi umbral de éxito (0.4) está POR DEBAJO del p95 del nulo, y mi falsador (0.2) jamás se dispararía. Estaría midiendo la subida de la bolsa y llamándola estacionalidad.
2. **No hay poder estadístico.** SE(Ŝ) ≈ √((1+S²/2)/T). In-sample (12 años, S≈0.35): SE ≈ 0.30. Falsador (0.2) y éxito (0.4) están a 0.67 SE → indistinguibles. Holdout (3 años): SE ≈ 0.59 → sólo puede REFUTAR un colapso, nunca confirmar. Falta el estado `underpowered`.
3. **La hipótesis y el falsador miden cosas distintas.** La hipótesis dice que el retorno se CONCENTRA en la ventana (test de medias, ~3000 días, alto poder); el falsador mide el Sharpe de una estrategia negociable (~576 días expuestos, bajo poder). Son dos preguntas: ¿existe el efecto? y ¿es explotable? Deben testearse por separado.

Más dos correcciones menores: el caveat de recorte por max_gross es innecesario (apalancamiento esperado ~1.15×, lejos del tope de 4 → convertirlo en tripwire de bug), y la cita está desalineada (Ariel 1987 vs McConnell-Xu 2008 con un solo año/URL).

## What Changes

Se edita SÓLO `hypotheses/H003_seasonality.yaml` (sigue `pre_registrado`, `intentos_realizados: 0`):

- **`estadistico_primario`** (existencia): contraste de medias del retorno diario en días TOM vs no-TOM, por instrumento y agrupado, con SE por bloques (block bootstrap). Reporta la diferencia en bps/día + IC 95%. Es el test de la hipótesis TAL COMO ESTÁ ESCRITA, con toda la muestra.
- **`benchmark_nulo`**: mismos índices, mismo sizing, mismo nº de días/mes (4), pero en días ALEATORIOS. 1000 remuestreos, semilla fija. Distribución del Sharpe nulo.
- **`FALSADOR` relativo**: si el Sharpe neto de TOM NO supera el p95 del nulo → muerta (retorno atribuible al drift, no a estacionalidad). El Sharpe absoluto es diagnóstico económico, NO falsador.
- **`poder_estadistico`**: SE in-sample (0.30) y holdout (0.59); requisito de reportar Sharpe con IC 95%; estado `underpowered` (IC cruza 0.2 y 0.4) → INDETERMINADO, ni muerta ni viable; el holdout sólo refuta ("consistente", nunca "confirmado").
- **`sizing`**: quitar el caveat de recorte; convertirlo en **tripwire** (recorte observado = bug, no limitación).
- **`fuente`**: separar Ariel (1987) y McConnell-Xu (2008), cada una con su año y URL.
- **`resultado_esperado`**: reencuadrar — el Sharpe absoluto (~0.3-0.5) es casi todo beta; la cantidad real es el EXCESO sobre el nulo, probablemente pequeño/indistinguible.

Fuera de alcance: implementar la señal, correr, tocar el holdout.

## Capabilities

### New/Modified Capabilities
<!-- Ninguna: artefacto de proyecto. skip_specs=true. -->

## Impact

- **Artefacto editado**: `hypotheses/H003_seasonality.yaml` (sigue `pre_registrado`). Verdadero test falsable por primera vez.
- **Sin código ni spec.** Legítimo pre-ejecución; tras el primer test se congela.
