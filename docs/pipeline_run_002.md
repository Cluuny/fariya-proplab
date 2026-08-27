# Pipeline de investigación — corrida 002 (eje operabilidad + rebalanceo de fuentes)

**Fecha:** 2026-08-26. **Modo:** E1-E3 deterministas en batch (`scripts/pipeline_run_002.py`,
DB persistente sembrada con la run 001); E4-E5 EN SESIÓN por Claude Code, sin API. **Cap:** 40
candidatos nuevos (contador 51→91/200). **NO se pre-registra ninguna hipótesis — sólo se
producen candidatos.** Holdout intacto, API no cableada.

Dos cambios respecto a la 001, ambos motivados por sus hallazgos:
1. **Décimo eje `es_estrategia_operable`** en E2.5 (determinista, sobre el abstract, ANTES del
   adversario). Mata el modo de muerte dominante de la 001 («no es una estrategia, es método/
   teoría/modelo/monitor»). Regla clave — **exige un verbo de EJECUCIÓN o una familia nombrada;
   `predict`/`signal` a secas NO bastan** (lección propia H003/OFI: predecir ≠ negociar).
2. **Rebalanceo de fuentes**: +Quantpedia (estrategias ya destiladas), arXiv con cuota menor,
   se procesan las no-arXiv primero. Métrica nueva: **densidad de estrategias operables por
   fuente**.

---

## D1. Embudo por estación

| estación | entraron | pasaron | murieron | causa dominante |
|---|---|---|---|---|
| E1 descubrimiento | — | 117 nuevos | — | arXiv 53 + microestructura 54 + Quantpedia 10 (AA/CXO 0: feeds sin novedad desde 001) |
| E1 cap (procesar) | 117 | 40 | 77 sin procesar | cap 40, no-arXiv primero → arXiv toma la cuota menor |
| E2 operabilidad | 40 | 13 | **27** | operabilidad (cross-sectional, opciones, sin regla) |
| **E2.5 es_estrategia_operable** | 13 | 5 | **8** | **NUEVO: método/teoría/modelo/monitor/tooling** |
| E3 costes | 5 | 5 (**1 keep** · 4 requiere_lectura) | 0 | — |
| E4 extracción (sesión) | 5 | **1** | 4 | no es estrategia operable (fugas del eje: índice, modelo, tooling, HFT) |
| E5 adversario (sesión) | 1 | 1 (keep, con flags) | 0 | — |
| → compuerta | 1 | **1** | — | Sectoral Intramonth Momentum (Quantpedia) |

**Lo que cambió respecto a la 001:** el décimo eje movió el filtro AGUAS ARRIBA. En la 001, 10
no-estrategias llegaban a sesión (E4); aquí **E2.5 mató 8 de forma determinista**, y sólo 5
llegaron a sesión (de los cuales 4 eran fugas que E4 atrapó). El trabajo de sesión bajó ~a la
mitad. **El eje NO es hermético** (ver D4): caza lo blatante (RL, generativo, optimización,
tests) pero deja pasar ÍNDICES / MODELOS / TOOLING que usan vocabulario de estrategia; E4 sigue
siendo el respaldo.

---

## D2. Densidad de estrategias operables por fuente — el número que dice DÓNDE buscar

**Densidad (eje) = pasan es_estrategia_operable / descubiertos-procesados:**

| fuente | descubiertos | pasan el eje | densidad (eje) | estrategias REALES tras E4 | densidad REAL |
|---|---|---|---|---|---|
| **quantpedia** | 10 | 2 | **20%** | 1 (Sectoral Momentum) | **10%** |
| arxiv | 30 | 3 | 10% | 0 | 0% |

**Quantpedia densifica el DOBLE que arXiv al nivel del eje (20% vs 10%), y ∞ más tras E4 (1 vs
0 estrategias reales).** Confirma la hipótesis del rebalanceo: una base de estrategias YA
destiladas produce más reglas operables que un repositorio de preprints (mayoritariamente
metodología). **Recomendación: subir Quantpedia y las fuentes aplicadas en las próximas
corridas; arXiv rinde poco por candidato leído.** Caveat honesto: el feed de Quantpedia mezcla
estrategias con posts de PRODUCTO/newsletter (2 de sus 3 supervivientes del eje eran posts de
API/benchmarking que E4 descartó); la densidad-eje sobreestima, la densidad-real es el número
duro.

SSRN quedó FUERA del rebalanceo automático: no tiene API pública (las «alertas por autor» son
manuales). Alpha Architect y CXO no aportaron novedades (feeds sin cambios desde la 001, un día
antes) — su cadencia es lenta; el rebalanceo real de esta corrida lo cargó Quantpedia.

---

## D3. El candidato que llega a la compuerta

**Llega UNO — y es el PRIMERO en la historia viva del pipeline que SUPERA el triaje de costes
(E3).** Ficha:

### C1 — Sectoral Intramonth Momentum Cycle (Quantpedia; Nathan/Suominen/Tasa 2026 a nivel sector)

- **fuente:** quantpedia (blog, estrategia destilada) · **clase:** precio/calendario · **frecuencia:** EOD · **prioridad:** 1.41
- **hipótesis:** ciclo de momentum intramensual en ETFs sectoriales US: el momentum sectorial
  trailing-252d da spread positivo el PRIMER día de mes, se REVIERTE en los días 2-3, y una
  tercera pata aparece 10-5 días antes de fin de mes. Componer las tres patas.
- **regla_entrada/salida:** secuencia calendárica de 3 patas (long-short y market-neutral) sobre
  los 9 Select Sector SPDR + SPY, Dic 1998–Jun 2026.
- **mecanismo:** momentum sectorial + estacionalidad de calendario intramensual.
- **bruto_reportado:** **0.55** (long-short) / 0.54 (market-neutral). **cita:** abstract
  («…at a 0.55 Sharpe ratio…»). (La extracción del número ANTES de «Sharpe» se arregló en esta
  corrida — antes se perdía; ver defectos abajo.)
- **duty estimado:** 0.15 (keyword «turn-of-the-month»; el abstract dice «invertido menos de la
  mitad de los días» → el duty REAL es mayor, ~0.4, pero no cambia el veredicto de coste).
- **bruto_requerido (E3):** CFD **0.436** / futuros 0.40 al duty estimado → **0.55 SUPERA → keep.**
  Primer candidato del pipeline vivo que despeja el suelo de costes en el cribado.
- **FALSADOR (escribible):** «si el exceso sobre el nulo de calendario (barajado de días) ≈ 0, o
  el Sharpe deflactado (DSR con las 3 patas) < listón, se descarta.»
- **findings del adversario (E5, 9 ejes):**
  - `periodo_descubrimiento`: **parcial** — in-sample 1998-2026; extiende a sectores un hallazgo
    de acciones individuales de 2026 (algo de independencia), pero el ajuste es sobre la misma muestra.
  - `n_variantes`: **FALLA (no crítico, pero es EL riesgo)** — «properly sequenced», «stitching
    three legs together»: 3 patas con timing elegido = alta multiplicidad. El 0.55 es un Sharpe
    de backtest SIN DEFLACTAR.
  - `sesgo_supervivencia`: **supera** — 9 SPDR sectoriales + SPY, universo estable.
  - `datos_no_rt`: **supera** — momentum trailing + calendario, todo ex-ante.
  - `costes_plausibles`: **supera el cribado (0.55 > 0.44)** — PERO el margen es fino y el 0.55 es
    in-sample; deflactado probablemente cae bajo el listón.
  - `contemporaneo_vs_predictivo`: **supera** — predictivo (calendario/momentum ex-ante).
  - `benchmark_cero`: **supera** — reporta long-short Y market-neutral.
  - `nulo_preserva_geometria`: n/a (sin nulo en el abstract; el falsador exige un nulo de calendario).
  - **hallazgo_no_enumerado:** «el candidato que SUPERA el coste es justo el más expuesto al
    SOBREAJUSTE de backtest: 3 patas calendáricas secuenciadas, Sharpe 0.55 SIN deflactar. Es
    exactamente lo que el paper MinervaScore (surgido en ESTE mismo lote y muerto en E2.5) existe
    para descontar (Deflated Sharpe / PBO). Y los efectos de turn-of-the-month YA murieron sobre
    NUESTROS datos (H003: exceso ≈ 0, IC cruza 0). Un candidato para leer con el DSR en la mano.»
- **veredicto E5:** keep → llega a la compuerta, **con bandera roja de multiplicidad/deflación**.

**Recomendación al operador:** leer íntegro; tratar el 0.55 como COTA SUPERIOR; exigir el Sharpe
deflactado (3 patas) y un nulo de calendario antes de considerar pre-registro. NO se pre-registra
en esta corrida (fuera de alcance). Relación directa con [[h003-tsmom-falsified]]-style turn-of-month.

---

## D4. Campo `hallazgo_no_enumerado` — todos + fugas del eje

Sólo C1 llegó a E5 (su `hallazgo_no_enumerado` arriba). Las otras 4 supervivientes de E2.5 son
**fugas del eje** que E4 atrapó — informan del ALCANCE del eje determinista:

| fuga | qué es | por qué el eje la dejó pasar |
|---|---|---|
| arxiv:2608.10788 Triadic Stress Index | ÍNDICE de estrés sistémico (detección de crisis) | menciona mercados/correlación; no dispara descalificador |
| quantpedia From Backtest to Benchmark | TOOLING (artículo sobre la API de Quantpedia para benchmarkear) | discute «trading rule»/«anomaly»/«trend-following» → dispara un positivo |
| arxiv:2608.07709 Rough Hawkes-Heston | MODELO de volatilidad rugosa (teoría) | vocabulario de microestructura; sin descalificador limpio |
| arxiv:2608.04373 Public Trader Identity | PREDICTIBILIDAD a 1 s en un DEX (R² 12.31%) con identidad de wallet | «return predictability»/«order flow»; es predictivo pero a 1 s = régimen OFI |

**Meta-hallazgo:** el eje `es_estrategia_operable` caza lo BLATANTE (RL, generativo,
optimización, tests: 8 muertos en E2.5) pero deja pasar ÍNDICES / MODELOS / TOOLING / estudios
de PREDICTIBILIDAD que usan vocabulario de estrategia. **Refinamiento propuesto para run 003**
(no implementado): descalificar «index/model/estimator» como OBJETO del título, y — la lección
del programa — tratar predictibilidad a horizonte de segundos como régimen HFT/OFI (sub-coste)
salvo prueba de neteo. El de Public Trader Identity es notable: predictibilidad REAL (R² 12.31%,
t=9.2) pero a 1 s y con datos de un DEX específico = el mismo régimen que cerró el order flow.

---

## D5. Triaje de costes — con los números

| candidato | fuente | frec | duty | bruto | requerido | veredicto E3 |
|---|---|---|---|---|---|---|
| Sectoral Intramonth Momentum | quantpedia | EOD | 0.15 | **0.55** | CFD 0.44 / fut 0.40 | **keep** (0.55 > 0.44) |
| From Backtest to Benchmark | quantpedia | EOD | 1.0 | — | CFD 0.64 | requiere_lectura |
| Triadic Stress Index | arxiv | EOD | 1.0 | — | CFD 0.64 | requiere_lectura |
| Rough Hawkes-Heston | arxiv | orderbook | — | — | intradía 9.17 (ES proxy) | requiere_lectura |
| Public Trader Identity | arxiv | orderbook | — | — | intradía 9.17 (ES proxy) | requiere_lectura |

Los 4 `requiere_lectura` no reportan Sharpe en el abstract (regla anti-alucinación: sin cifra →
no se descarta, baja prioridad). Los dos `orderbook` reciben el requerido intradía ~9.17 (ES
proxy): coherente con que la alta frecuencia exige un bruto descomunal.

---

## D6. Contador de la condición de parada

**91 / 200.** (backfill 11 + run001 40 + run002 40). DB persistente `data/pipeline/research.db`
(gitignored), sembrada con la run 001 para acumular honestamente. Quedan 109.

---

## D7. Coste de sesión — el eje pagó

- **A sesión llegaron 5** (vs 11 en la 001), gracias a E2.5. De ésas, 4 se resolvieron a
  abstract (fugas no-estrategia) y 1 (Sectoral Momentum) mereció lectura atenta. **El décimo eje
  recortó el trabajo de sesión ~55%** (11→5 supervivientes; y de los 5, sólo 1 exige PDF).
- **Extrapolación a 200:** con E2.5 filtrando el no-estrategia barato, el cuello de sesión pasa a
  ser ~1 lectura de PDF por corrida (el candidato que despeja coste). 200 candidatos ≈ ~5 corridas
  de cribado + ~5 lecturas íntegras. Alcanzable en modo sesión SIN API — el eje cambió la aritmética.
- **Decisión sobre la API:** la 002 produjo **1 candidato que supera el cribado de costes**
  (Sectoral Momentum), pero con bandera roja de deflación (in-sample, 3 patas). No es «candidato
  útil» suficiente para justificar cablear la API todavía; sí para **subir Quantpedia**. **API
  sigue sin cablear.**

---

## Defectos deterministas hallados por la corrida 002 (con test)

1. **Extracción del Sharpe:** no capturaba el número ANTES de «Sharpe» («0.55 Sharpe ratio»,
   frasing muy común) → sólo «Sharpe … 0.55». Arreglado con un segundo patrón + guardia
   anti-porcentaje (evita tomar «5.99% … Sharpe» como Sharpe). Sin el fix, el ÚNICO candidato que
   supera el coste se habría quedado en `requiere_lectura` en vez de `keep`.
2. **Eje poroso (registrado, no un bug):** deja pasar índices/modelos/tooling; refinamiento
   propuesto para run 003 (arriba).

---

## Resumen ejecutivo

- El décimo eje `es_estrategia_operable` FUNCIONA: mató 8 no-estrategias determinista, recortó el
  trabajo de sesión ~55%. Regla `predecir ≠ negociar` (sin «predict»/«signal» a secas) — lección
  propia H003/OFI codificada.
- **Densidad por fuente: Quantpedia 20% (eje) / 10% (real) vs arXiv 10% / 0%.** Quantpedia es
  donde buscar; arXiv rinde poco por lectura.
- Primer candidato de la historia viva que SUPERA el cribado de costes: Sectoral Intramonth
  Momentum (0.55 > 0.44), pero es un Sharpe de backtest sin deflactar, 3 patas calendáricas, y el
  turn-of-month ya murió en H003 → bandera roja de sobreajuste. NO pre-registrado.
- Contador 91/200. API no cableada. Holdout intacto. Cero pre-registros.
- El eje no es hermético (fugas: índice, modelo, tooling, HFT-predictibilidad); E4 las atrapó;
  refinamiento propuesto para run 003.
