# Pipeline de investigación — corrida 001 (primera corrida real, papers ciegos)

**Fecha:** 2026-08-26. **Modo:** E1-E3 deterministas en batch (`scripts/pipeline_run_001.py`);
E4 (extracción) y E5 (adversario) corridas EN SESIÓN por Claude Code, sin API — mismo patrón
que `docs/extraction_validation.md`. **Cap:** 40 candidatos procesados por E1-E3 (no se consume
la cuota de la condición de parada de 200). **Fuentes E1:** arXiv q-fin PM/ST/TR + barrido de
microestructura (q-fin.TR AND términos) + RSS Alpha Architect + RSS CXO Advisory. **Reglas
anti-alucinación activas en E4** (cita-o-null, figura→null, sin-falsador→rechazo) y el noveno
eje del adversario (`nulo_preserva_geometria`, de H008). **NO se pre-registra ninguna hipótesis
en esta corrida — sólo se producen candidatos.** El holdout no se toca. La API no se cablea.

Es la primera vez que el pipeline procesa papers que no conocíamos. También es el TEST CIEGO del
adversario que no se pudo montar aparte (sección 4).

---

## D1. Embudo por estación — lo más importante

| estación | entraron | pasaron | murieron | causa dominante |
|---|---|---|---|---|
| E1 descubrimiento | — | 101 descubiertos | — | arXiv 50 + microestructura 38 + Alpha Architect 5 + CXO 8 |
| E1 cap (procesar) | 101 | 40 (más recientes) | 61 sin procesar | cap de 40 (no consumir la cuota de 200) |
| E2 operabilidad | 40 | 11 | **29** | **operabilidad 28 · falsabilidad 1** |
| E2.5 estimación | 11 | 11 | 0 | determinista (frecuencia/duty/bruto-si-está) |
| E3 costes | 11 | 11 (0 keep · **11 requiere_lectura**) | **0** | el abstract NO reporta Sharpe → nadie muere aquí |
| E4 extracción (sesión) | 11 | **1** | **10** | **sin FALSADOR escribible / no es una estrategia operable** |
| E5 adversario (sesión) | 1 | 1 (keep) | 0 | — |
| → compuerta | 1 | **1** | — | el único candidato operable de la corrida |

**La pregunta de fondo del programa — ¿el cuello es el SUMINISTRO de ideas o el ACCESO a
datos/vehículo? — se responde, con un matiz que no esperábamos:**

1. **El suministro NO es el cuello.** E1 descubrió 101 candidatos en un mes de una sola pasada.
2. **En abstract, el filtro que muerde NO es el de costes (E3) sino el de OPERABILIDAD (E2).**
   La predicción «90%+ muere en E3» NO se cumple sobre arXiv: **E3 mató 0**, porque los abstracts
   de q-fin casi nunca reportan un Sharpe → todos caen en `requiere_lectura`, no en `reject`. El
   coste no puede decidir sin el número, y el número está en el PDF, no en el abstract.
3. **El cuello REAL, revelado al leer (E4), es que la mayor parte de q-fin no son estrategias
   operables:** de 11 supervivientes, **10 son METODOLOGÍA / TEORÍA / OPTIMIZACIÓN / MODELOS
   GENERATIVOS / MONITORES DE RIESGO / ANÁLISIS DE FONDOS**, no reglas direccionales con falsador.
   El filtro que los mata es la regla anti-alucinación de E4 (sin FALSADOR → rechazo), no el coste.
4. **El único candidato operable de la corrida (crypto short-horizon mean reversion, D3) reporta
   en su propio abstract un edge bruto de 1.3 bp/trade contra un coste de 5 bp/round-trip — es
   decir, muere por coste por su propia evidencia.** Un grupo independiente acaba de medir, sobre
   cripto, el MISMO muro de costes que este programa ya había encontrado (OFI, H008). El acceso a
   datos/vehículo se confirma como el cuello — desde fuera.

**En una frase:** el suministro de ideas es abundante; lo escaso es (a) que sean estrategias
operables y no métodos, y (b) que la única operable supere el suelo de costes — que no lo hace.

---

## D2. Tasa de rechazo por tipo de fuente

| tipo_de_fuente | n | rechazados (E2) | % | nota |
|---|---|---|---|---|
| preprint (arXiv) | 27 | 18 | 67% | rechazos: cross-sectional de acciones, optimización, opciones, métodos puros |
| blog (Alpha Architect + CXO) | 13 | 11 | 85% | rechazos: análisis de ETFs, ciclos electorales, comentario — casi nada operable en prop |
| paper_arbitrado | 0 | — | — | arXiv marca preprint; ResearchGate/SSRN (arbitrados) quedan para ingesta manual |

Los blogs rechazan más (85% vs 67%): confirman ser fuente de COMENTARIO más que de reglas
operables — pero pasan por los mismos filtros y su tasa se MIDE, no se asume (2 de 13 sobreviven:
los dos resúmenes de CXO sobre LETFs/convertibles, que igualmente mueren en E4 por no ser reglas).

---

## D3. Los candidatos que llegan a la compuerta

**Llega UNO.** (Se esperaban 3-5; el resultado es 1, y ése es el hallazgo.) Ficha completa:

### C1 — Short-horizon mean reversion in cryptocurrency markets (arxiv:2608.21888)

- **tipo_de_fuente:** preprint · **clase_de_dato:** flujo · **frecuencia:** intradía (15 min) · **prioridad:** 1.3
- **hipótesis:** a horizontes de 15 min, el retorno direccional revierte en cripto mucho más y
  más pervasivamente que en acciones US; «apostar contra la vela previa» captura la mayor parte
  del efecto (la señal vive en los SIGNOS, no en las magnitudes; autocorrelación lag-1 ≈ 0).
- **regla_entrada:** fade del signo de la vela de 15 min previa (short tras vela up, long tras
  vela down), en perpetuos/spot de cripto.
- **regla_salida:** horizonte de 15 min (siguiente vela).
- **mecanismo económico:** provisión de liquidez COMPENSADA — la reversión se concentra tras
  movimientos impulsados por flujo TAKER agresivo y crece con la intensidad del flujo; la
  profundidad del libro consumida no condiciona nada («consistent with compensated liquidity
  provision, not a test that selects it»). Mecanismo coherente y del lado correcto.
- **clase_de_dato / datos:** cripto (Binance, 183 pares), tape propio; gratis (ya lo ingerimos).
- **duty / turnover:** intradía, alto turnover (fade cada 15 min → ~96 rt/día si continuo).
- **bruto_reportado:** **null** (regla anti-alucinación: el abstract da el edge en **bp/trade**,
  no en Sharpe; no se convierte ni se inventa). **cita del número real:** abstract — «the gross
  edge peaks near **1.3 bp per trade** against a **5 bp round-trip cost**». `requiere_lectura_manual`
  para el Sharpe (si el PDF lo reporta, y en qué tabla).
- **bruto_requerido calculado:** suelo intradía de referencia (ES proxy, 50 rt/día) = **9.17** de
  Sharpe; el suelo cripto real es otro (maker+funding evitado), pero el veredicto no depende de la
  cifra exacta: **el propio paper dice 1.3 bp < 5 bp → NETO NEGATIVO**. No despeja el coste.
- **FALSADOR (escribible):** «si el edge bruto por trade < coste de round-trip para nuestro
  vehículo/fees, se descarta» — y el paper ya lo reporta refutado (1.3 < 5). Falsable y falsado
  por su propia evidencia.
- **findings del adversario (E5, 9 ejes):**
  - `periodo_descubrimiento`: **supera** — protocolo estrictamente out-of-sample + holdout congelado de 6 meses.
  - `n_variantes`: **supera** — «one matched protocol», sin barrido reportado; pre-registrado.
  - `sesgo_supervivencia`: **supera** — 183 pares Binance + 187 acciones/ETFs US, no un universo curado.
  - `datos_no_rt`: **supera** — señal sobre la vela previa (disponible en tiempo real).
  - `costes_plausibles`: **FALLA (no crítico aquí porque el paper YA lo reconoce)** — 5 bp RT es el
    coste que usan y el edge (1.3 bp) no lo supera; honesto.
  - `degradacion_post_pub`: n/a (paper de 2026, sin post-historia).
  - `contemporaneo_vs_predictivo`: **supera** — es PREDICTIVO (apuesta sobre la vela SIGUIENTE), con null de permutación.
  - `benchmark_cero`: **supera** — compara contra «benchmark spot capture costs», no contra un beta compartido.
  - `nulo_preserva_geometria` (eje nuevo H008): **supera** — usa un null de PERMUTACIÓN EXACTA
    sobre los signos; para una apuesta de signo, permutar signos preserva la geometría de la
    estrategia (no es el fallo de H008 de aleatorizar la entrada sin reponer objetivo/stop).
  - **hallazgo_no_enumerado:** «el paper es una MEDICIÓN HONESTA, no un pitch: concluye
    explícitamente que el edge es *large enough to detect, too small to clear costs*. Replica,
    desde una fuente independiente, el veredicto de order-flow-cerrado del programa (OFI/H008):
    en cripto de alta frecuencia hay señal real pero sub-coste.»
- **veredicto E5:** keep (llega a la compuerta) — **pero es un candidato PRE-REFUTADO por su
  propio coste reportado.** Valor real: confirmación externa e independiente del muro de costes.

**Recomendación al operador:** NO pre-registrar (el paper ya reporta neto negativo). Registrar
como EVIDENCIA EXTERNA que corrobora [[program-verdict-and-futures]] / order-flow cerrado.

---

## D4. Campo `hallazgo_no_enumerado` — todos los que se llenaron

Sólo C1 llegó a E5, así que sólo hay un `hallazgo_no_enumerado` de candidato (arriba: «medición
honesta, replica order-flow-cerrado»). Pero la corrida produjo un **hallazgo_no_enumerado de
NIVEL DE SISTEMA**, que es el resultado más importante para el alcance del adversario:

> **Los 9 ejes del adversario PRESUPONEN que el candidato ES una estrategia** (tienen ejes para
> período, variantes, supervivencia, look-ahead, costes, benchmark, geometría del nulo…). **No
> tienen ningún eje para «esto no es una estrategia operable, es un método / teoría / modelo
> generativo / monitor de riesgo».** Y ése fue el modo de muerte DOMINANTE de la corrida (10 de
> 11). Lo atrapó la regla de FALSADOR de E4 (schema), no el adversario. Es un hueco real del
> adversario, medido sobre papers ciegos — candidato a un décimo eje (sección 4).

---

## D5. Los que «murieron en E3» — con el número

**Ninguno murió en E3.** Los 11 supervivientes de E2 quedaron en `requiere_lectura` porque su
abstract no reporta un Sharpe (regla: sin bruto → no se descarta, baja prioridad). Es auditable
que E3 corrió y computó el requerido para cada uno (sólo que ninguno tenía cifra que contrastar):

| candidato | frecuencia | duty est. | requerido (CFD/fut o intradía) | bruto en abstract |
|---|---|---|---|---|
| arxiv:2608.23416 Axiomatic Trader | EOD | 1.0 | 0.64 / 0.42 | — (teoría) |
| arxiv:2608.23808 MinervaScore | EOD | 1.0 | 0.64 / 0.42 | — (métrica de backtest) |
| arxiv:2608.20727 Multiscale Ball Test | EOD | 1.0 | 0.64 / 0.42 | — (test econométrico) |
| arxiv:2608.20179 CVaR Portfolio Opt | EOD | 1.0 | 0.64 / 0.42 | — (optimización) |
| arxiv:2608.19389 Concentrated Liquidity RL | EOD | 1.0 | 0.64 / 0.42 | — (RL / DeFi LP) |
| cxo LETFs | EOD | 1.0 | 0.64 / 0.42 | — (análisis de LETFs) |
| cxo Convertible Bond ETFs | EOD | 1.0 | 0.64 / 0.42 | — (análisis de fondos) |
| arxiv:2608.22768 Loop-Gain Matrix | orderbook | — | intradía 9.17 (ES proxy) | — (monitor de estabilidad) |
| arxiv:2608.21888 Crypto mean reversion | orderbook | — | intradía 9.17 (ES proxy) | **1.3 bp/trade < 5 bp coste** (bp, no Sharpe) |
| arxiv:2608.18195 Multi-Level MM RL | orderbook | — | intradía 9.17 (ES proxy) | — (RL market making) |
| arxiv:2608.13096 FlowLOB | orderbook | — | intradía 9.17 (ES proxy) | — (generador de LOB) |

Los cuatro `orderbook` reciben un requerido intradía ~9.17 (ES como proxy; el suelo cripto real
difiere) — cifra enorme que, correctamente, marca que una estrategia de alta frecuencia necesita
un bruto descomunal para netear tras rotar. Coherente con el veredicto de order flow.

**Diagnóstico de por qué E4 mató a 10 (lo que un abstract sí basta para juzgar):**

| candidato | por qué NO es una hipótesis operable (E4: sin falsador) |
|---|---|
| Axiomatic Trader | Teoría: «cinco constantes que declarar»; no hay regla ni edge, es un meta-marco. |
| MinervaScore | Métrica de robustez de backtests (Deflated Sharpe + PBO + SPA + MinTRL). Es una HERRAMIENTA (útil), no una estrategia. |
| Multiscale Ball Test | Test de independencia de media condicional; econometría pura. (De hecho: «remove every full-sample rejection» → dependencia contemporánea, no predictiva — eco del OFI.) |
| CVaR Portfolio Opt | Control continuo con restricción CVaR; recupera Merton. Optimización, no edge; además transversal. |
| Concentrated Liquidity RL | Provisión de liquidez en UniswapV3 vía RL. Política de caja negra (sin falsador escribible), DeFi LP, no direccional. |
| CXO LETFs / Convertible ETFs | Análisis de costes/rendimiento de fondos; no una regla operable. |
| Loop-Gain Matrix | Monitor de estabilidad sistémica de complejos LETF (radio espectral); riesgo, no trading. |
| Multi-Level MM RL | Market making con RL en el libro. Caja negra + el MM es inviable a nuestras fees (maker 2 bp vs spread 0.03 bp, `docs/crypto_pivot.md`). |
| FlowLOB | Generador de trayectorias de LOB (flow matching). Simulador de datos, no estrategia. |

---

## D6. Contador de la condición de parada

**51 / 200.** (backfill 11 + esta corrida 40). Quedan 149 antes de la condición de parada.
Nota: el contador es acumulativo del programa; esta corrida gastó 40 deliberadamente (no más).

---

## D7. Coste de sesión — ¿es 200 alcanzable en este modo?

- **Procesados en sesión (E4-E5):** 11 abstracts leídos + fichados + pasados por los 9 ejes.
- **Tokens de lectura (aprox):** ~6k tokens de abstracts (los 11) + razonamiento de extracción y
  adversario. A NIVEL DE ABSTRACT, ~40 candidatos/sesión es holgado.
- **PERO la lectura comprometida es del PDF ÍNTEGRO** (sección 4). Un PDF de q-fin ≈ 10-25k tokens.
  A ese nivel: **~5-10 papers por sesión** antes de fatiga/contexto. Los 11 de esta corrida a
  abstract fueron baratos porque 10 se descartan sin abrir el PDF (no son estrategias); sólo C1
  merecía lectura íntegra.
- **Extrapolación a 200:** si el 25-30% sobrevive a E2 (11/40 aquí) y de ésos casi todos se
  resuelven a abstract (no-estrategia) salvo ~1 que exige PDF, entonces 200 candidatos ≈ **~5
  sesiones a nivel abstract + ~5-10 lecturas íntegras de PDF**. Alcanzable en modo sesión, tedioso
  pero no prohibitivo — MIENTRAS la cosecha de candidatos operables siga siendo ~1 cada 40.
- **Decisión sobre la API:** la API (`make_api_extractor`) se cablea SÓLO si una corrida produce
  candidatos ÚTILES que justifiquen automatizar. **Esta corrida no lo hizo** (0 candidatos
  operables que superen costes; 1 pre-refuted). **Conclusión: NO cablear la API todavía.** El seam
  queda documentado y sin conectar. Consecuencia registrada: en este modo el pipeline NO es
  automatizable (sin cron ni lotes desatendidos); cada corrida requiere sesión interactiva.

---

## Sección 4. Lectura humana comprometida + métrica del alcance del adversario

**Compromiso (`docs/extraction_defects.md`):** los candidatos que llegan a la compuerta se leen
ÍNTEGROS por el operador aunque el adversario diga KEEP. En esta corrida llega **1** (C1). El
operador debe leer arxiv:2608.21888 completo.

**MÉTRICA — problemas reales que la lectura encontró y el adversario (9 ejes) NO enumeró:**

En modo sesión, Claude actuó como adversario (E5) Y como lector cuidadoso (proxy del operador;
la lectura íntegra final la hace Vicente). Los problemas que la LECTURA encontró y que ningún eje
del adversario habría reportado por sí solo:

1. **«No es una estrategia» (10 de 11 candidatos).** Ningún eje pregunta si el candidato es
   siquiera una regla operable; los 9 asumen que sí. Lo atrapó E4 (falsador), no E5. **Ratio: el
   modo de muerte dominante de la corrida está FUERA de los 9 ejes.**
2. **«Caja negra sin falsador» (RL: 2608.19389, 2608.18195).** Una política de RL no tiene regla
   escribible que refutar; el adversario, dado un ficha con «regla = política RL», no tendría eje
   para objetarlo. Es un sub-caso de (1).
3. **Para C1, la lectura CONFIRMA al adversario** (no lo contradice): el `costes_plausibles`
   falla y el paper lo reconoce. Aquí el operador NO encontró un problema que el adversario
   ocultara — el adversario y la lectura coinciden. Buen signo para el alcance del adversario EN
   candidatos que sí son estrategias.

**Lectura de la métrica:** el adversario es adecuado CUANDO el candidato ya es una estrategia
operable (en C1 coincide con la lectura). Su hueco es anterior: no distingue estrategia de
método. Propuesta concreta (no se implementa en esta corrida, sólo se registra): **décimo eje
`es_estrategia_operable` — “¿el paper propone una REGLA direccional con entrada/salida, o es un
método / test / optimización / modelo generativo / monitor?”**. Es el eje que esta corrida ciega
demostró que falta, con 10 casos concretos.

---

## Resumen ejecutivo

- Suministro abundante (101 en una pasada); el cuello NO es la escasez de ideas.
- En abstract, muerde E2 (operabilidad), no E3 (costes): arXiv no reporta Sharpes en el abstract,
  así que la predicción «90% muere en costes» no aplica a este nivel — el coste decide al leer.
- Al leer, 10 de 11 no son estrategias operables (métodos/teoría/RL/generativos/monitores).
- El único candidato operable (crypto mean reversion 15 min) reporta su propio edge (1.3 bp) por
  DEBAJO del coste (5 bp): confirmación externa e independiente del muro de costes de order flow.
- Contador 51/200. API NO cableada (sin candidatos útiles). Holdout intacto. Cero pre-registros.
- Defectos del pipeline hallados y corregidos por esta corrida: (a) arXiv `http`→`https`; (b)
  barrido de microestructura mal formado (400) + sin AND-scope (traía física); (c) falso positivo
  de falsabilidad por el acrónimo `ict` como subcadena de `predict`/`explicit`. Los tres con test.
- Hueco del adversario medido: le falta el eje «¿es una estrategia operable?» (10 casos).
