# Recap completo del programa

## Why

El programa está cerrado (tag v1.2-closed) y documentado en piezas (`program_verdict.md`,
`terrain_breadth.md`, `funded_*`, `pipeline_*`, `pre_run_003_calibration.md`). Falta UN documento
autosuficiente que se lea de una sentada y permita AUDITAR el programa entero —cada afirmación con
su número y su `archivo:línea`— sin abrir el código. Y una sección nueva que responda por qué las
curvas espectaculares que se ven por ahí no contradicen el cierre.

## What Changes

**`docs/RECAP.md`** (sólo documentación), como auditoría:
1. **Cronología** por bloque (motor→pipeline): qué se construyó, qué resolvía, qué reveló —
   incluidos los bugs que cada capa expuso (hardening del simulador, barra de domingo, retorno
   cruzado de hueco, los bugs de subcadena).
2. **Las nueve familias:** señal, mecanismo, universo/período, medido, por qué murió con el número,
   expectativa comprometida, y la CAUSA REAL tras la relectura (≥5 por amplitud).
3. **Los cinco cierres independientes**, cada uno recalculable a mano (suelo de costes, amplitud,
   economía del payout, volatilidad, tasa del pipeline), con el número que reabriría cada uno.
4. **Sección NUEVA — por qué las curvas que se ven por ahí no contradicen esto:** generadores tipo
   StrategyQuant vs deflated Sharpe (factor 0.35); curvas sin IC (Sectoral IC95 [0.17,0.93]);
   sesgo de supervivencia con la aritmética propia; y qué evidencia SÍ contradiría el cierre.
5. **Lo que SÍ funcionó** (motor validado, simulador verificado, diversificación por familia,
   hallazgos propios, validación externa, las seis refutaciones medidas).
6. **Los sesgos que el programa corrigió en sí mismo** (P(quemar)≈0, ancla +0.057, coincidencia
   mal emparejada, nulo con geometría rota).
7. **El mapa de lo que falta** (restricciones con su precio + las tres condiciones de reapertura
   con su número actual).

Todo con citas `archivo:línea` verificadas contra el código.

## Impact

- NUEVO: `docs/RECAP.md`. Sin cambios de código; holdout intacto; sin pre-registro.
