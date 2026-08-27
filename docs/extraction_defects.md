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

## Estado (tras change provenance-corrections, 2026-08-24)

| defecto | estado |
|---|---|
| D1 período MOP 1965 → 1985-2009 | **CORREGIDO** (fichas H001/H007 + enmiendas; registro de aprendizaje) |
| D2 Sharpe 1.2 sin cita → null | **CORREGIDO** + **regla (c) de figuras** codificada (abajo) |
| D3 falsador inútil | mitigado por compuerta humana (el esquema no lo atrapa; requiere lectura) |
| D4 benchmark = beta | cubierto por el eje crítico `benchmark_cero` del adversario |

**Regla nueva (c) — numéricos que sólo están en figuras** (`extract.py`): si un valor sólo
aparece en una figura/gráfico (no en texto ni tabla), se emite **null** y se marca
`requiere_lectura_manual: true` con nota de qué figura lo contiene. Visible en el reporte de
la compuerta humana (estación 7). Test que verifica null+flag (no valor inventado).

**Registro de aprendizaje:** H001 y H007 tienen `ancla_defectuosa: 1` (su bruto_esperado se
derivó del 1.2 mal citado). El reporte recalcula el sesgo de calibración con y sin ellas y
concluye **NO HAY CALIBRACIÓN TODAVÍA** (el +0.057 previo no era evidencia limpia del marco).

## Nota de honestidad sobre la validación misma

El extractor y el adversario fueron el **MISMO modelo** en la corrida de validación
(`docs/extraction_validation.md`). Que el adversario rechazara TOM (beta) y OFI
(contemporáneo) es buena señal, pero **ambos ejes estaban en la lista que le dimos**, y esa
lista salió de errores que YA conocíamos. **NO está demostrado que el adversario detecte un
fallo NO anticipado.** Ese test sólo llega con papers nuevos.

**MITIGACIÓN COMPROMETIDA (actualizada tras el test ciego, ver abajo):** los primeros **40
candidatos** de la corrida real se leen ÍNTEGROS por el operador, aunque el adversario diga
KEEP. Recién después se confía en el filtro adversario sin lectura completa.

## Test ciego del adversario (change adversarial-blind-test, 2026-08-24)

Se buscó un eje que NO le enseñamos al adversario y ver si lo detecta solo. Sustituto: AQR,
"A Century of Evidence on Trend-Following Investing" (Hurst, **Ooi & Pedersen**, 2017;
`hurst2017_trend.pdf`). **Eje ciego:** Ooi y Pedersen son 2 de los 3 autores de
Moskowitz-Ooi-Pedersen (2012) → una "confirmación" del trend firmada por los mismos autores
del hallazgo original NO es independiente. Ese conflicto no estaba en los 8 ejes.

**RESULTADO: NO DETECTADO.** Sin interpretar a favor, por dos razones:
1. **Contaminación de este experimento:** el operador reveló el eje ciego en el MISMO prompt
   que corría el adversario (el mismo modelo). No puedo auto-certificar "detección espontánea"
   habiendo sido informado. Un test ciego limpio exige que el adversario NO haya visto la
   respuesta — sólo se puede correr en una sesión futura que no lo sepa.
2. **Límite ESTRUCTURAL (lo más importante):** el adversario implementado (`adversarial.evaluate`)
   sólo acepta un `findings` dict con las claves de `ATTACK_QUESTIONS`. **No hay canal para una
   objeción novel** como la no-independencia autoral: aunque un modelo la notara, el sistema no
   podría registrarla. Con los 8 ejes originales, AQR pasaba como KEEP (sólo se marcaba
   degradación); el conflicto autoral, el "material de gestora no arbitrado" y la calidad de
   datos de las décadas tempranas quedaban FUERA.

**Evidencia sobre el alcance del adversario (no aprobado/suspenso):** el adversario caza lo que
enumeramos; un fallo genuinamente NO anticipado no tiene dónde registrarse y no hay garantía de
que se detecte. De ahí la lectura humana íntegra de los primeros 40.

**Remediación aplicada (rama "no detectado"):**
- Mitigación 20 → **40** candidatos leídos íntegros.
- Dos ejes NUEVOS en la estación 5 (`adversarial.ATTACK_QUESTIONS`):
  `autores_independientes` (¿los autores son los mismos del hallazgo original?) y
  `literatura_previa_posterior` (¿qué dice la literatura previa/posterior?). Con ellos
  explícitos, AQR ya marca `autores_independientes` (y `sesgo_supervivencia` por la calidad de
  datos del siglo) — pero eso es porque AÑADIMOS el eje, no porque el adversario lo descubriera.

## Corrida 001 (papers ciegos) — el test ciego real del adversario

`docs/pipeline_run_001.md` (2026-08-26) es el test ciego que no se pudo montar aparte: la
primera corrida sobre papers que nadie había visto. Resultado sobre el ALCANCE del adversario:

- **Coincidencia en estrategias reales:** el único candidato operable (crypto mean reversion 15
  min, arxiv:2608.21888) — la lectura CONFIRMA al adversario (`costes_plausibles` falla y el
  paper lo reconoce; 1.3 bp < 5 bp). El operador no encontró un problema oculto por el adversario.
- **Hueco medido, NO enumerado:** el modo de muerte DOMINANTE (10 de 11 supervivientes de E2) fue
  «no es una estrategia operable» (método / teoría / RL caja-negra / modelo generativo / monitor
  de riesgo). **Ningún eje del adversario pregunta eso** — lo atrapó la regla de FALSADOR de E4,
  no la estación 5. Los 9 ejes presuponen que el candidato ya es una estrategia.
- **Propuesta registrada (no implementada aún):** décimo eje `es_estrategia_operable` — «¿el
  paper propone una REGLA direccional con entrada/salida, o es un método/test/optimización/modelo
  generativo/monitor?». Es el eje que la corrida ciega demostró que falta, con 10 casos concretos.
