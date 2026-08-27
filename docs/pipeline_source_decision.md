# Decisión de fuentes del pipeline — el caso Quantpedia Premium (SIN decidir)

**Fecha:** 2026-08-26. **Estado: PENDIENTE — escrito para reposar, NO decidido.** Este documento
registra el caso con los números MEDIDOS (runs 001-002), no lo resuelve. Se revisa más adelante.

## Densidad de estrategias operables por fuente (runs 001-002)

El número que dice dónde buscar, MEDIDO (no una corazonada):

| fuente | densidad (eje) | densidad real (tras E4) | nota |
|---|---|---|---|
| **Quantpedia** | 20% | **10%** | estrategias ya destiladas; el feed gratis mezcla producto/newsletter |
| arXiv | 10% | **0%** | mayoritariamente metodología; 0 estrategias operables reales en 2 runs |
| Alpha Architect + CXO | — | — | sin novedad entre runs (cadencia lenta; RSS pequeño) |
| SSRN | — | — | sin API pública → ingesta manual, no escalable |

Quantpedia es la única fuente con densidad real > 0 en dos corridas. Es donde hay estrategias
operables por unidad de lectura.

## La opción

**Suscribir Quantpedia Premium** (~900 estrategias destiladas, con métricas out-of-sample ya
calculadas y API disponible). Cabe en el presupuesto de $125/mes.

## Argumento A FAVOR

- **Es la primera vez en el programa que un gasto se apoyaría en una densidad MEDIDA, no en una
  corazonada.** Todo el ciclo CFD y el pivote a cripto se decidieron por argumentos; ésta sería
  la primera decisión de datos con un número detrás (10% real Quantpedia vs 0% arXiv).
- **Cambiaría la relación señal/ruido del pipeline:** procesar estrategias YA destiladas con
  Sharpe reportado y métricas out-of-sample, en vez de leer papers de metodología de los que el
  90%+ no es siquiera una estrategia (el modo de muerte dominante de la run 001).
- La API permitiría automatizar E1-E3 sobre estrategias estructuradas (Sharpe, universo, regla ya
  en campos), reduciendo el cuello de sesión — y daría el benchmark de «¿es esto redundante con una
  estrategia ya documentada?» de forma sistemática (justo lo que el post «From Backtest to
  Benchmark» describía).

## Argumento EN CONTRA

- **Dos corridas y 91 candidatos han producido UN candidato**, con **bandera roja de sobreajuste**
  (Sectoral Intramonth Momentum: 0.55 in-sample, 3 patas calendáricas) y que además **muere en el
  cribado aritmético** (`docs/candidate_sectoral_screen.md`: IC incluye el listón; deflación;
  exposición compartida con el mercado). Más volumen de la MISMA calidad no cambia el listón.
- Quantpedia reporta Sharpes **in-sample / de backtest**; el programa ya sabe (H008, MinervaScore,
  este cribado) que un Sharpe reportado sin deflactar no sobrevive el cribado propio. 900
  estrategias destiladas son 900 Sharpes que habrá que deflactar y cribar igual — el trabajo caro
  (el cribado) no lo hace Quantpedia.
- El cuello del programa NUNCA fue el suministro de ideas (la run 001 lo confirmó: 101 candidatos
  en una pasada). Fue el ACCESO a datos/vehículo con un edge sobre el suelo de costes. Quantpedia
  da más ideas, no más acceso ni más edge.

## No decidir todavía

El caso está escrito. **No se decide en este change.** Se deja reposar: la próxima corrida (003,
con el eje refinado) y una revisión del reviewer darán más señal sobre si la densidad de Quantpedia
se sostiene y si alguno de sus candidatos sobrevive al cribado aritmético — que es la prueba real,
no el Sharpe reportado. La regla del programa se mantiene: **un gasto se justifica por una densidad
medida Y por al menos un candidato que sobreviva el cribado propio, no sólo por volumen.** Hasta
hoy, cero candidatos han sobrevivido el cribado. Revisar tras la run 003.
