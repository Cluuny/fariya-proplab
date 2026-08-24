# Manual de defectos del extractor (y de nuestras fichas manuales)

Defectos hallados al validar la extracción contra casos conocidos
(`docs/extraction_validation.md`). Se corrigen ANTES de procesar candidatos nuevos.

Hallazgo central: la validación no destapó defectos del EXTRACTOR (que se comportó bien:
disciplina anti-alucinación operativa, adversario acertado), sino de nuestras **fichas
MANUALES** — precisamente lo que un conjunto de validación debe hacer.

## D1 — Período de MOP: "1965-2009" es impreciso (real: 1985-2009)

- **Dónde:** `hypotheses/H001_tsmom.yaml`, `hypotheses/H007_tsmom_expanded.yaml`
  (`periodo_original: "1965-2009"`).
- **Qué dice el paper:** el resultado PRIMARIO es **1985-2009** (§4.1 p.16: "sample period
  1985 to 2009"; §2.3 p.15: "we report results post-1985"). El 1965 aparece SÓLO como
  robustez: "similar results if older data is included going back to 1965, but ... we report
  results post-1985."
- **Impacto:** menor para el veredicto (H001/H007 murieron por coste, no por período), pero es
  una imprecisión de procedencia. **Corrección:** anotar "1985-2009 (primario); 1965-2009
  (datos extendidos, robustez)".

## D2 — Sharpe reportado de MOP: "1.2" sin cita de ubicación verificable

- **Dónde:** las fichas de trend citan `sharpe_reportado: 1.2` como el número del paper.
- **Qué pasó:** el Sharpe del factor diversificado está en **Figure 2** (gráfico de Sharpe por
  contrato), no en texto extraíble. El extractor, por la regla (a), **NO emitió** 1.2 (lo puso
  null). No pude verificar en las páginas leídas una cita textual que contenga "1.2".
- **Impacto:** nuestras fichas afirman un número sin apuntar a una ubicación que lo contenga —
  exactamente lo que la regla (a) prohíbe. **Corrección:** o bien citar la figura/tabla exacta
  que lo contiene tras verificarla, o marcar el Sharpe como "en Figure 2, no verificado en
  texto". No propagar 1.2 como si fuera una cita.

## D3 — Falsador inútil: el defecto que la validación de esquema NO atrapa

- **Observación (no un defecto de una ficha concreta, sino una regla de operación):** un
  falsador tipo "si la estrategia no funciona se descarta" PASA la validación de esquema
  (es un string no vacío) y es INÚTIL porque no puede dispararse con un criterio medible.
- **Por qué importa:** es la razón por la que la estación 4 no se puede dejar 100% automática.
  El esquema garantiza que EXISTE un falsador; sólo un humano/adversario garantiza que sea
  FIRABLE (un corte numérico sobre una métrica).
- **Corrección/operación:** la compuerta humana (estación 7) revisa que cada falsador tenga un
  umbral medible antes de aprobar. Los tres falsadores extraídos aquí sí son firables (cortes
  de Sharpe/R²/exceso-sobre-nulo).

## D4 — Benchmark de TOM: beta de mercado disfrazada de estacionalidad

- **Dónde:** conceptual, relevante a H003 y a cualquier candidato long-only de calendario.
- **Qué:** el "exceso de retorno" de McConnell & Xu en la ventana TOM se captura estando
  LARGO del mercado 4 días/mes → es beta de mercado concentrada, no un edge market-neutral.
  El adversario lo marcó como fallo CRÍTICO (`benchmark_cero`).
- **Corrección/operación:** todo candidato de calendario/long-only debe medirse contra el NULO
  (p. ej. 4 días aleatorios), no contra cero — la lección de H003 ya codificada como eje
  crítico del adversario.

## Estado

Ninguno bloquea automatizar la extracción; D1/D2 corrigen procedencia de fichas propias,
D3/D4 son reglas de operación ya codificadas (regla a; eje crítico del adversario). La
extracción se declara VÁLIDA para la corrida real (change siguiente, con API key).
