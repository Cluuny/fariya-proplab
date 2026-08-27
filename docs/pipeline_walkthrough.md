# El pipeline de investigación, punta a punta

Este documento explica el sistema completo en prosa, para que puedas delegarle la búsqueda de
estrategias **sabiendo dónde NO confiar en él**. Cita rutas y funciones concretas
(`archivo:línea`) para que verifiques cualquier afirmación contra el código. No hace falta leer el
código para entenderlo; sí para auditarlo.

**Qué es, en una frase.** Una cola ordenable de hipótesis (SQLite, no un chatbot) que descubre
candidatos de fuentes públicas, los pasa por filtros deterministas baratos que matan lo que no
podemos operar o pagar, y sólo lleva los supervivientes a una lectura cara (extracción + revisión
adversaria). El objetivo NO es encontrar estrategias: es **matar cada idea por la razón correcta,
barato, antes de gastar un intento**.

---

## Diagrama de flujo (con los conteos REALES de las corridas 001 y 002)

```
                                   RUN 001            RUN 002
                                   (2026-08-26)       (2026-08-26, con E2.5)
E1  DESCUBRIMIENTO   ──────────►   101 descubiertos   117 descubiertos
    (arXiv + RSS + manual)         └─ 40 procesados   └─ 40 procesados   (cap; no gastar la cuota de 200)
                                        │                   │
E2  OPERABILIDAD     ──────────►   mata 29            mata 27            (¿podemos operarlo y pagarlo?)
    (heurística determinista)           │                   │
                                        │                   │
E2.5 ¿ES ESTRATEGIA? ─────────►   (no existía)        mata 8             (¿es una regla, o un método/teoría?)
    + estimación de campos               │                   │
                                        │                   │
E3  COSTES          ──────────►   0 reject           0 reject           (¿el bruto reportado despeja el listón?)
    (aritmética pura)              11 requiere_lectura 1 keep + 4 req_lectura
                                        │                   │
                                   ─────┴─────          ─────┴─────
E4  EXTRACCIÓN (SESIÓN) ───────►  11 leídos           5 leídos           (PDF → ficha; reglas anti-alucinación)
E5  ADVERSARIO (SESIÓN) ───────►  10 mueren           4 mueren           (11 ejes de ataque)
                                        │                   │
COMPUERTA HUMANA    ──────────►   1 candidato         1 candidato        (el operador lee ÍNTEGRO)
                                   (crypto mean-rev)   (Sectoral Momentum)
                                        │                   │
DESTINO             ──────────►   pre-refutado        MUERE en el cribado
                                   (edge 1.3bp<5bp)    aritmético (IC incluye el listón)
```

**Lectura del diagrama:** de 40 candidatos procesados, ~29 mueren en E2 (no operables), ~8 en E2.5
(no son estrategias), y de los pocos que llegan a sesión casi todos mueren al leerlos. En dos
corridas (91 candidatos) **cero sobrevivieron el cribado propio.** El cuello NUNCA fue el
suministro de ideas.

---

## (1) El recorrido de tres candidatos reales

### (a) Muerte en E2 — «Cross-Sectional Heterogeneity in LSTM Networks» (arxiv:2608.05755)

- **Qué entra:** un dict con `titulo`, `abstract`, `url`, `fecha`, `fuente`, `tipo_de_fuente`
  (`discover.parse_arxiv_atom`, `src/pipeline/discover.py:76`). Abstract real:
  > «Predicting financial asset returns... standard architectures often struggle to account for the
  > **cross-sectional heterogeneity** of asset returns. This paper proposes a novel architectural
  > extension to the basic LSTM...»
- **Qué se le hace:** `triage_operability` (`src/pipeline/triage_operability.py:103`) baja el texto
  a minúsculas y busca palabras clave de universo NO operable.
- **Qué sale:** `reject`, categoría `operabilidad`, razón literal **«cross-sectional de acciones
  (señal: 'cross-section')»**. Estado → `rechazada_operabilidad`.
- **Qué lo mató:** la sección transversal de acciones necesita >100 instrumentos con universo
  point-in-time — no operable en prop. Muerte CORRECTA. (No llegó a E2.5/E3.)

### (b) Muerte en E2.5 — «AI-Driven Multiscenario Interest Rate Forecasting» (arxiv:2608.12424)

- **Qué entra:** superó E2 (menciona «forecasting», «asset management» — nada que dispare el
  filtro de operabilidad).
- **Qué se le hace:** `estimate.is_operable_strategy` (`src/pipeline/estimate.py:261`) pregunta si
  el abstract describe una POSICIÓN direccional. Abstract real:
  > «...developing an AI-supported prototype for multiperspective interest rate **forecasting**...
  > It integrates topic modeling, sentiment analysis, econometric forecasting...»
- **Qué sale:** `reject`, razón **«sin regla de entrada/salida direccional identificable en el
  abstract»**. Estado → `rechazada_no_estrategia`, causa `no_estrategia`.
- **Qué lo mató:** es un PRONÓSTICO / prototipo, no una estrategia. Predecir ≠ negociar (la lección
  de H003/OFI está codificada: `predict`/`signal` a secas NO cuentan como regla; ver
  `estimate.py:242`). Muerte CORRECTA — y es exactamente el modo de muerte dominante que la run 001
  no tenía cómo atrapar (llegaba a sesión).

### (c) El único que llegó a E3 y a la compuerta — «Sectoral Intramonth Momentum Cycle» (Quantpedia)

- **E2:** pasa (es una estrategia de momentum sectorial, universo pequeño de ETFs).
- **E2.5:** pasa — el abstract dice «trailing 252-day sector momentum», «long-short», «anomaly»:
  posición direccional clara (`estimate._STRATEGY_RULE`, `estimate.py:242`).
- **Estimación (E2.5):** `estimate.estimate_fields` (`estimate.py:180`) fija frecuencia=EOD,
  duty≈0.15 (keyword «turn-of-the-month»), y extrae el Sharpe del abstract por regex
  (`extract_bruto_reportado`, `estimate.py:151`): encuentra **«0.55 Sharpe»** → `bruto_reportado=0.55`,
  `cita_bruto="abstract (\"0.55 Sharpe\")"`.
- **E3 costes** (`triage_costs.triage_costs`, `src/pipeline/triage_costs.py:76`): listón CFD al duty
  estimado = 0.44. **0.55 > 0.44 → `keep`.** Primer candidato de la historia viva que despeja E3.
  Llega a la compuerta con prioridad 1.41 (`estimate.priority_score`, `estimate.py:291`).
- **Destino — muere en el cribado aritmético** (`docs/candidate_sectoral_screen.md`, SIN backtest):
  el IC del Sharpe [0.17, 0.93] INCLUYE el listón 0.44 (irresoluble incluso con 27.5 años);
  deflación a N≈50-100 alcanza el listón; el turn-of-month ≈ beta de mercado (problema de H003).
  Veredicto: **cribado_muere.** No se pre-registró.

**Moraleja de los tres:** los filtros baratos (E2, E2.5) matan la enorme mayoría por la razón
correcta; el único que pasó al cribado caro murió por aritmética, no por backtest. El sistema
antepone lo barato a lo caro en todo momento.

---

## (2) Descubrimiento (E1) — de dónde salen los candidatos

Todo en `src/pipeline/discover.py`. La red se toca sólo en `fetch_*`; el parseo es puro y testeable.

| fuente | acceso | consulta exacta | por corrida | cadencia |
|---|---|---|---|---|
| **arXiv (categorías)** | API Atom (`fetch_arxiv`, `discover.py:106`) | `cat:q-fin.PM OR cat:q-fin.ST OR cat:q-fin.TR`, orden por fecha desc (`ARXIV_CATS`, `discover.py:28`) | ~50-80 | mensual (cron) |
| **arXiv (microestructura)** | misma API, AND-scoped | `(cat:q-fin.TR) AND (all:"order flow imbalance" OR "market microstructure" OR "limit order book" OR "price impact" OR "VPIN" OR "trade classification" OR "high frequency")` (`MICROSTRUCTURE_TERMS`, `discover.py:31`) | ~30-50 | mensual |
| **Alpha Architect** | RSS (`fetch_rss`, `discover.py:143`) | feed completo `alphaarchitect.com/feed/` | ~5 | lento (semanal) |
| **CXO Advisory** | RSS | `cxoadvisory.com/feed/` | ~8 | lento |
| **Quantpedia** | RSS | `quantpedia.com/feed/` (`RSS_FEEDS`, `discover.py:35`) | ~10 | lento |
| **SSRN / Reddit / Twitter / Discord / YouTube** | MANUAL (`manual_candidate`, `discover.py:149`) | URL pegada a mano; el tipo de fuente etiqueta el origen | 0 automático | a demanda |

**Densidad medida de estrategias operables por fuente (runs 001-002):** Quantpedia **20% (eje) /
10% (real tras leer)** vs arXiv **10% / 0%**. arXiv es mayoritariamente metodología; Quantpedia son
estrategias ya destiladas (pero su feed mezcla posts de producto/newsletter que mueren en E2/E2.5).
**El número dice dónde buscar: Quantpedia densifica; arXiv rinde poco por lectura.**

**Puntos ciegos (qué NO cubre):**
- **SSRN** no tiene API pública → sólo ingesta manual (`manual_candidate`), no escalable.
- **arXiv q-fin** es el único repositorio con API limpia; papers en journals de pago, o en SSRN
  detrás de login, no entran solos.
- **Contenido no-académico** (un hilo de Twitter, un vídeo de YouTube, un libro, un post de Discord)
  entra SÓLO si el operador pega la URL con `manual_candidate(url, titulo, abstract,
  tipo_de_fuente=...)`. Pasa por los MISMOS filtros; su tasa de rechazo por tipo de fuente es un
  RESULTADO que se mide, no se asume. Si mencionas una fuente, así entra: la resumes en un abstract
  y la registras a mano; el pipeline no lee vídeos ni PDFs de libros por su cuenta.

---

## (3) Los filtros — qué mata cada uno, con la regla literal

### E2 — Operabilidad (`triage_operability.py:103`)

Heurística determinista sobre `título + abstract` en minúsculas. Rechaza, en orden:
1. **No falsable** (categoría `falsabilidad`): palabras ICT/SMC (`_NON_FALSIFIABLE`,
   `triage_operability.py:38`): «order block», «fair value gap», «ict», «smc», «liquidity grab»,
   «institutional liquidity»… — se definen sobre el gráfico, sin dato externo que los refute.
   **Coinciden con LÍMITE DE PALABRA** (`_hits_word`) para no casar «ict» dentro de «predict».
2. **Cross-sectional de acciones** (`_CROSS_SECTIONAL`, `:45`): «cross-section», «stock returns»,
   «crsp», «compustat», «decile portfolio», «fama-macbeth»… → universo >100, no operable.
3. **Opciones / vol implícita** (`_NEEDS_OPTIONS`, `:51`): «option», «implied volatility», «vix»,
   «variance risk premium», «skew»…
4. **Fundamentales point-in-time** (`_NEEDS_FUNDAMENTALS`): «earnings announcement», «balance
   sheet», «accrual», «book-to-market»…
5. **Sin regla identificable**: si el abstract no contiene ninguna señal de `_HAS_RULE`
   (`:61`: «momentum», «carry», «mean reversion», «order flow», «volume profile», «trading rule»…)
   → `reject`.
6. **Presupuesto de datos** (`DATA_BUDGET_USD = 125`, `:31`): si el candidato declara
   `costo_datos_usd_mes > 125` → `rechazada_por_datos`.

**Mató 29/40 (run 001) y 27/40 (run 002)** — el filtro que más muerde en abstract.

**FALSOS POSITIVOS conocidos (mata lo que no debería):** el filtro por SUBCADENA de keywords
produce rechazos erróneos. Ejemplos reales de la run 002:
- «**Is Trend Still Your Friend?**» (un estudio real de trend-following sobre ~100 futuros) fue
  rechazado por «requiere fundamentales point-in-time (señal: **'fundamental'**)» — la palabra
  «fundamental» aparecía en otro sentido. Un paper OPERABLE muerto por un keyword.
- «Universality... Stylized Facts» — mismo falso positivo por «fundamental».
- «On a Simple Relationship Between Order Imbalance...» — rechazado por «requiere opciones (señal:
  **'skew'**)», pero el «skew» era del flujo de órdenes, no de opciones.

Los acrónimos cortos (ict/smc/fvg) YA usan límite de palabra (`_hits_word`) tras tres bugs de
subcadena (ict⊂predict, carry⊂carrying, long-the⊂along-the); pero las listas PERMISIVAS de
clasificación (fundamentals, options) aún casan por subcadena y pueden rechazar de más. **Sesgo del
filtro: prefiere matar de más (falso rechazo) que dejar pasar basura — un falso rechazo se pierde,
pero no contamina la cola.**

### E2.5 — ¿Es una estrategia operable? + estimación (`estimate.py`)

Dos pasos sobre los que pasan E2:
1. **`is_operable_strategy`** (`estimate.py:261`): rechaza salvo que el abstract describa una
   POSICIÓN direccional. (a) descalificadores de método/teoría/modelo/monitor/tooling
   (`_NOT_STRATEGY`, `:218`: «reinforcement learning», «portfolio optimization», «generative
   model», «robustness grade», «benchmark dataset»…); (b) rechazo por HORIZONTE inoperable <1min
   (`_INOPERABLE_HORIZON`, `:234`: «millisecond», «one-second», «high-frequency»…); (c) exige una
   señal de regla (`_STRATEGY_RULE`, `:242`: verbos de ejecución o familias nombradas). **Todo con
   límite de palabra.** `predict`/`signal` a secas NO bastan.
2. **`estimate_fields`** (`estimate.py:180`): puebla los campos que E3 necesita, DETERMINISTA:
   - `frecuencia` por keywords (order book → orderbook; intraday/high-frequency → intraday_bar; si
     no, EOD).
   - `duty_cycle_estimado`: 1.0 por defecto; **0.15** si hay keyword de calendario/evento
     («turn-of-the-month», «seasonal», «earnings»…). Estimación grosera, documentada.
   - `turnover_estimado`, `clase_de_dato`, y para intradía `trades_por_dia_estimado` + `contrato_ref`.
   - `bruto_reportado`: regex del Sharpe SÓLO si está en el abstract (`extract_bruto_reportado`,
     `:151`), con guardia anti-porcentaje; captura «Sharpe of X» y «X Sharpe». Ausente → `None`.

**Mató 8/40 (run 002; no existía en run 001).**

**FALSOS POSITIVOS del eje (deja pasar lo que no debería):** en la run 002 el eje dejó pasar 4
no-estrategias que E4 tuvo que atrapar: un índice de estrés, un modelo de vol rugosa, un post de
tooling de Quantpedia, y un estudio de predictibilidad HFT a 1s. Tres de esos cuatro leaks eran
BUGS DE SUBCADENA (carry⊂carrying, long-the⊂along-the) — corregidos con `_hits_word`; el cuarto
(tooling) necesitó un descalificador meta. Aun refinado, el eje deja pasar índices/modelos/tooling
que usan vocabulario de estrategia — **E4 (la lectura) es el respaldo, no el eje.**

### E3 — Costes (`triage_costs.py:76`)

Aritmética pura, sin datos nuevos. Rutea por frecuencia:
- **EOD:** listón = `bruto_requerido(duty, vehiculo)` (`triage_costs.py:55`), que llama a
  `costs_model.sharpe_bruto_requerido_duty` con `UMBRAL_NETO = 0.40` (`:34`) y el break-even del
  vehículo (`VEHICULOS`, `:30`: CFD 0.24 → requerido **0.64** a duty 1.0; futuros 0.024 → **0.42**).
  Se evalúa contra AMBOS vehículos.
- **Intradía:** listón por rotación (`costs_model.sharpe_bruto_requerido_intraday`), donde lo
  domina rotar, no mantener.
- **Regla común:** `bruto_reportado` ausente → **`requiere_lectura`** (no se descarta, baja
  prioridad); `> requerido` → `keep`; `<= requerido` → `reject`.

**De dónde salen duty y turnover:** de `estimate_fields` (E2.5), por keywords — son ESTIMACIONES
del abstract, no del paper. El duty por defecto (1.0, o 0.15 si calendario) puede estar lejos del
real (H008: 0.20 a priori → 0.31 medido). **Qué pasa cuando el abstract no reporta Sharpe:** casi
siempre (arXiv no reporta Sharpe en el abstract) → `requiere_lectura`. Por eso **E3 mató 0 en
ambas corridas**: no puede decidir sin el número, y el número está en el PDF. El coste decide al
LEER, no en el cribado. (Cuando el número SÍ está —Sectoral 0.55— E3 sí decide.)

---

## (4) Extracción (E4) — de PDF a ficha

**Estado real: E4 es un SEAM, NO cableado a una API.** `extract_from_pdf(path, llm)`
(`src/pipeline/extract.py:78`) levanta `NotImplementedError` si no se inyecta un `llm`. En las
corridas 001 y 002, la extracción la hizo **Claude Code EN SESIÓN leyendo los abstracts** (mismo
patrón que `docs/extraction_validation.md`), no un modelo por API sobre el PDF entero. Consecuencia
registrada: en este modo el pipeline NO es automatizable (cada corrida requiere sesión).

- **Qué se le pasaría al modelo (contrato del seam):** `llm(pdf_text) → dict` con los campos de la
  ficha + un `cita_<campo>` por cada numérico. En sesión, lo que se leyó fueron los ABSTRACTS
  (~300-500 palabras), no PDFs completos (~10-25k tokens). El PDF íntegro es la lectura del OPERADOR.
- **El prompt literal:** no hay uno cableado — el seam documenta el contrato, no un prompt de
  producción. Cuando se conecte, el prompt debe forzar structured output y exigir la cita por
  numérico. (No se inventa aquí para no fingir que existe.)
- **El esquema de la ficha** (la validación, `validate_extraction`, `extract.py:39`) exige los
  campos mínimos de una hipótesis (`REQUIRED_FIELDS`, `:28`): `titulo`, `familia`, `mecanismo`,
  `hipotesis`, `regla_entrada`, `falsador`. El esquema completo de la fila vive en la DB
  (`db.py:57`, tabla `hipotesis`): identidad, clasificación, frecuencia/datos, triaje de costes,
  registro de aprendizaje (`bruto_esperado`/`bruto_medido`/`duty_cycle_real`), y los campos de E4-E5
  (`cita_bruto`, `requiere_lectura_manual`, `adversarial_veredicto`).
- **Las dos reglas anti-alucinación, cómo están IMPLEMENTADAS** (`validate_extraction`,
  `extract.py:39-75`):
  - **(a) cita-o-null:** cada campo de `NUMERIC_FIELDS_REQUIRING_CITATION` (`:26`, hoy
    `{bruto_reportado: cita_bruto}`) sin una `cita_<campo>` no vacía → el número se pone a `None` y
    se registra en `dropped_fields`; se marca `requiere_lectura_manual=1`. (Regla de figuras: un
    número que sólo está en una figura no tiene cita de texto → cae por esta misma vía. Caso real:
    el Sharpe 1.2 de Moskowitz está en la Figura 2 → se dejó en null, no se inventó.)
  - **(b) sin-falsador → rechazo:** si `falsador` no es un string escribible → `accepted=False`,
    razón «sin FALSADOR escribible → rechazado por esquema». Impide acumular «ideas interesantes».
- **Qué pasa cuando el modelo devuelve algo que no valida:** `validate_extraction` devuelve
  `accepted=False` con `reject_reason`; el candidato NO entra a la cola. Los numéricos sin cita se
  anulan (no se rechaza todo por eso, sólo se pierde el número). Es lo que evita que la basura pase.

---

## (5) Adversario (E5) — los ejes de ataque

Un segundo agente con un único trabajo: **DESTRUIR la ficha** (los LLM son aduladores; un revisor
que sólo busca fallos contrarresta ese sesgo). `src/pipeline/adversarial.py`. Hoy hay **11 ejes**
en `ATTACK_QUESTIONS` (`:18`). Si CUALQUIER eje CRÍTICO falla → `reject` (`evaluate`, `:50`).

| # | eje (clave) | pregunta literal | ¿crítico? | de dónde salió |
|---|---|---|---|---|
| 1 | `periodo_descubrimiento` | ¿backtest en el mismo período donde se descubrió el efecto? | **SÍ** | clásico |
| 2 | `n_variantes` | ¿cuántas variantes probaron antes de reportar ESTA? (multiplicidad) | flag | clásico |
| 3 | `sesgo_supervivencia` | ¿sesgo de supervivencia en el universo? | **SÍ** | clásico |
| 4 | `datos_no_rt` | ¿usa datos no disponibles en tiempo real (look-ahead)? | **SÍ** | clásico |
| 5 | `costes_plausibles` | ¿costes plausibles para nuestro tamaño y broker? | **SÍ** | suelo de costes |
| 6 | `degradacion_post_pub` | ¿evidencia post-publicación de degradación? | flag | clásico |
| 7 | `contemporaneo_vs_predictivo` | ¿el resultado es CONTEMPORÁNEO o PREDICTIVO? | **SÍ** | **error propio: H003/OFI** (describir≠predecir) |
| 8 | `benchmark_cero` | ¿el benchmark es CERO o comparte la exposición de la estrategia? | **SÍ** | **error propio: H003** (su Sharpe ERA el beta) |
| 9 | `autores_independientes` | ¿los autores del paper son los mismos del hallazgo original? | flag | **test ciego (AQR)** |
| 10 | `literatura_previa_posterior` | ¿existe literatura previa o posterior sobre este efecto? | flag | test ciego |
| 11 | `nulo_preserva_geometria` | si hay benchmark nulo: ¿preserva la GEOMETRÍA de la estrategia, o sólo aleatoriza la entrada? | **SÍ** | **error propio: H008** (nulo defectuoso) |

**7 críticos, 4 flag.** Cinco de los once nacieron de ERRORES PROPIOS del programa: el adversario
es, en parte, una lista de las trampas en las que ya caímos.

**`hallazgo_no_enumerado`:** un campo libre donde el adversario registra un problema FUERA de la
lista. Se ha llenado: en la run 001, el meta-hallazgo «el candidato es una medición honesta que
replica el muro de order-flow» (arxiv:2608.21888); y a nivel de sistema, «los 9/11 ejes presuponen
que hay estrategia — no hay eje para *esto no es una estrategia*», lo que motivó el eje E2.5. Es el
único canal por el que algo no anticipado puede quedar registrado.

**LIMITACIÓN CONOCIDA (documentar con claridad):** el adversario **sólo puede reportar lo que está
en la lista.** `evaluate` (`adversarial.py:50`) sólo mira las claves de `ATTACK_QUESTIONS`; un eje
novel no tiene canal (salvo `hallazgo_no_enumerado`, que depende de que el modelo lo note
espontáneamente). El **test ciego con el paper de AQR** (Hurst/Ooi/Pedersen 2017, cuyos autores son
2/3 de Moskowitz 2012 → no es replicación independiente) salió **NO DETECTADO**: con los 8 ejes de
entonces, AQR pasaba KEEP; sólo se atrapa la no-independencia porque DESPUÉS añadimos el eje. **El
adversario caza lo que enumeramos, no lo que no anticipamos.** Por eso la lectura humana íntegra.

---

## (6) Dónde puede engañarte el pipeline — la sección más importante

Modos de fallo CONOCIDOS, con lo que se hace (o no) al respecto:

1. **El extractor (E4) y el adversario (E5) son el MISMO modelo.** En sesión, Claude extrae y Claude
   ataca. Un fallo que el extractor no ve, el adversario tampoco. *Qué se hace:* la lectura humana
   íntegra de los candidatos que llegan a la compuerta (comprometida en `docs/extraction_defects.md`,
   primeros 40). *Qué NO se hace:* no hay dos modelos independientes.
2. **El adversario sólo caza lo enumerado.** Test ciego AQR = NO DETECTADO (arriba). *Qué se hace:*
   se añaden ejes cuando se descubre un hueco (ahora 11). *Qué NO:* no hay garantía de detectar un
   fallo NO anticipado; el `hallazgo_no_enumerado` depende de la suerte del modelo.
3. **Un falsador puede pasar el esquema y ser INÚTIL.** `validate_extraction` exige que `falsador`
   sea un string no vacío, no que sea BUENO. Un «se descarta si no funciona» pasa la validación.
   *Qué se hace:* la compuerta humana lo revisa (es el defecto D3 de `extraction_defects.md`).
4. **El Sharpe reportado puede ser in-sample, sin deflactar, y E3 lo toma TAL CUAL.** `bruto_reportado`
   es lo que dice el abstract; E3 no lo deflacta ni comprueba multiplicidad. El Sectoral Momentum
   pasó E3 con 0.55 y luego murió en el cribado aritmético (deflación, IC). *Qué se hace:* el cribado
   aritmético (`candidate_screen.py`) ANTES de pre-registrar. *Qué NO:* E3 por sí solo no protege
   contra un backtest sobreajustado.
5. **Bugs de subcadena de keywords.** Aparecieron TRES veces (ict⊂predict, carry⊂carrying,
   long-the⊂along-the) y causaron falsos rechazos (Is-Trend-Still-Your-Friend por «fundamental») y
   falsos positivos del eje. *Qué se hace:* los gates de DECISIÓN usan límite de palabra
   (`_hits_word`) + un test genérico (`tests/test_pipeline_word_boundary.py`). *Qué NO:* las listas
   permisivas de clasificación (fundamentals/options en E2) aún casan por subcadena → aún hay falsos
   rechazos posibles.

**La pregunta clave: si un candidato pasa TODAS las estaciones, ¿qué NO garantiza eso?**
- NO garantiza que la estrategia FUNCIONE — sólo que es operable, que su bruto REPORTADO despeja el
  listón, y que sobrevive 11 ejes conocidos. El Sharpe reportado puede ser humo (in-sample,
  sobreajustado); por eso sigue el cribado aritmético y, si sobrevive, el backtest propio con
  falsador pre-registrado y holdout.
- NO garantiza ausencia de un fallo NO anticipado (el adversario no lo vería).
- NO garantiza que el falsador sea bueno (sólo escribible).
- **Pasar el pipeline significa: "vale la pena gastar tiempo de sesión y quizá un intento en esto",
  no "esto tiene edge".** El pipeline reduce el espacio de búsqueda; no certifica una estrategia.
  El único juez de eso es el backtest propio contra el holdout, que ningún candidato ha alcanzado.

---

## (7) Qué hace falta para correrlo

**Comandos** (`scripts/pipeline.py`, CLI):
```bash
uv run python -m scripts.pipeline init          # crea el esquema SQLite
uv run python -m scripts.pipeline backfill      # carga las 11 hipótesis conocidas (validación)
uv run python -m scripts.pipeline discover      # E1: arXiv + RSS (cron MENSUAL)
uv run python -m scripts.pipeline triage        # E2 → E2.5 → E3 sobre los candidatos
uv run python -m scripts.pipeline report        # reporte de aprendizaje (densidad, supervivencia)
uv run python -m scripts.pipeline queue         # la siguiente hipótesis en cola
# corridas completas reproducibles con cap y semilla:
uv run python -m scripts.pipeline_run_002 --arxiv-max 80 --cap 40 --seed <run001.json> --json out.json
```

- **Determinista, SIN sesión (batch):** E1 (HTTP a arXiv/RSS), E2, E2.5, E3. Todo aritmética y
  keywords. Se puede correr desatendido; un cron mensual basta.
- **Requiere SESIÓN interactiva:** E4 (extracción) y E5 (adversario), porque el modelo lee en
  sesión y el seam de API no está cableado. NO hay cron ni lotes desatendidos para E4-E5.
- **Cuántos candidatos por sesión:** a nivel de ABSTRACT, ~40 caben holgados (las corridas 001/002
  procesaron 40 cada una). A nivel de PDF ÍNTEGRO (la lectura del operador), ~5-10 por sesión.
- **Dónde se guarda el estado si se interrumpe:** en la DB SQLite `data/pipeline/research.db`
  (`db.DEFAULT_DB_PATH`, `db.py:24`), gitignored y regenerable (el backfill es determinista). Cada
  candidato tiene un `estado` (`db.py`, columna `estado`); `discover` no re-inserta ids existentes
  (`db.get(...) is None`), así que una corrida interrumpida se retoma sin duplicar. `upsert`
  (`db.py:157`) es idempotente por `id`.
- **El contador de la condición de parada:** vive en la propia DB. `db.count_processed`
  (`db.py:213`) cuenta las filas con `estado != 'candidato'` (procesadas); el umbral es
  `db.N_CONDICION_PARADA = 200` (`db.py:130`). Se actualiza solo, al triar cada candidato. Estado
  actual: **91/200** (backfill 11 + run001 40 + run002 40). La condición de parada quedó SUPERADA
  por el cierre de amplitud (`docs/terrain_breadth.md`), no por llegar a 200.

---

## Resumen para quien delega la búsqueda

Confía en el pipeline para **descartar** barato y por la razón correcta: mata cross-sectional,
opciones, no-estrategias y bruto-bajo sin gastarte tiempo. **NO confíes en él para AFIRMAR** que
algo funciona: el Sharpe reportado puede ser humo, el adversario sólo ve lo enumerado, extractor y
adversario son el mismo modelo, y un falsador puede ser inútil pero válido. Todo lo que pasa el
pipeline va a un cribado aritmético y, si sobrevive, a un backtest propio con holdout — que es el
único juez. En 91 candidatos, cero llegaron tan lejos. El sistema hizo su trabajo: convirtió
«¿funciona X?» en un descarte barato y honesto, nueve veces y en toda una cola.
