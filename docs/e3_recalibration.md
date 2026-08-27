# Recalibración de E3 — factor de degradación, listón por estrategia, familia de riesgo

**Fecha:** 2026-08-26. **Modo:** cambio de código + retro-test sobre los 91 candidatos ya
procesados (SIN correr la run 003). Arregla los dos problemas de E3 documentados en
`docs/pipeline_walkthrough.md` §3 y §6.4.

**Los dos problemas:**
- **(A)** E3 mató 0 en ambas corridas — los abstracts de arXiv no reportan Sharpe, todo cae en
  `requiere_lectura`. El filtro no ahorra trabajo de sesión.
- **(B)** cuando SÍ decide, compara el bruto REPORTADO contra el listón sin descontar. Un Sharpe
  de paper es in-sample, sin deflactar, en otro mercado y sin nuestros costos ni amplitud. El
  Sectoral pasó E3 con 0.55 y murió después en el cribado con IC95 [0.17, 0.93].

---

## (1) Factor de degradación — calibrado con evidencia propia

`FACTOR_DEGRADACION = 0.35` (`src/costs_model.py`), aplicado al bruto reportado ANTES de
compararlo contra el listón. Es un factor **reportado → nuestro BRUTO realizado esperado** (NO
reportado→neto: el suelo de costes se aplica aparte). Derivación:

| referencia | reportado | nuestro bruto medido | ratio |
|---|---|---|---|
| TSMOM (Moskowitz-Ooi-Pedersen) | ~1.2 | 0.37 (H001-A) | 0.31 |
| TOM (McConnell-Xu) | efecto fuerte | 0.26 = media del nulo | ~0 |
| Sectoral Intramonth Momentum | 0.55 | IC95 [0.17, 0.93], punto ~0.4 | ~0.7 |
| Trend industria (SG CTA) | — | 0.32 bruto de comisiones | — |

Media defendible de las razones con número ≈ **0.35**. **PROVISIONAL** (3-4 puntos); se refina con
cada candidato testeado (el registro de aprendizaje guarda reportado vs medido).

**Regla nueva de E3** (`src/pipeline/triage_costs.py`):
```
bruto_efectivo = bruto_reportado × 0.35
keep si bruto_efectivo > bruto_requerido   (el requerido incluye el suelo de costes)
```

**Cuánto tiene que reportar un paper para sobrevivir E3** — con el suelo de costes DENTRO del
requerido (no se salta):

| vehículo | requerido (duty 1.0) | reportado necesario = requerido / 0.35 |
|---|---|---|
| Futuros | 0.42 | **≈ 1.20** |
| CFD | 0.64 | **≈ 1.83** |

**Nota de reconciliación honesta:** el bloque estimó «~1.15 bruto» comparando el efectivo contra
el 0.40 NETO directamente — pero eso SALTA el suelo de costes (el factor 0.35 es reportado→bruto,
no reportado→neto; TSMOM 1.2→0.37 es bruto, cuyo neto fue 0.08). La regla cost-coherente compara
contra el REQUERIDO (que ya lleva el 0.40 neto + el suelo de costes), y da **1.20 (futuros) / 1.83
(CFD)**. El **1.20 de futuros ≈ el 1.15 del bloque** — el número del bloque es el del vehículo de
futuros; en CFD el listón es más alto.

---

## (2) El listón correcto — 0.4 NETO por estrategia

`UMBRAL_NETO = 0.40` no cambia de valor, pero la RAZÓN es nueva (documentada en `triage_costs.py`):

> El objetivo NO es una estrategia con Sharpe 0.8. Es **CUATRO estrategias DESCORRELACIONADAS con
> Sharpe 0.4 cada una: 0.4 · √4 = 0.8.** Ésa es la única amplitud que el terreno no agota: la
> breadth (BR) viene de estrategias INDEPENDIENTES, no sólo de instrumentos. Cuatro estrategias
> descorrelacionadas sobre los mismos 17 instrumentos multiplican BR ×4.

Por tanto el listón POR CANDIDATO es **0.4 neto**, y hacen falta **CUATRO** que lo superen **Y que
no correlacionen entre sí** — de ahí el campo `familia_de_riesgo`.

---

## (3) Campo nuevo: `familia_de_riesgo`

`db.py` gana la columna `familia_de_riesgo` (vocab `FAMILIAS_DE_RIESGO`: trend, carry, reversion,
estacionalidad, flujo, volatilidad, macro, otra). `estimate.estimate_familia_de_riesgo` la clasifica
por palabras clave (con límite de palabra). El registro de aprendizaje
(`learning_report._por_familia_riesgo`) reporta **supervivientes por familia de riesgo**: si los
cuatro que hacen falta salen de la MISMA familia, no hay diversificación y el 0.8 no se alcanza.

**Defecto hallado y corregido en el retro-test:** «carry» a secas es un VERBO común («183 pairs
**carry** significant directional reversal») → clasificaba el paper de mean-reversion como carry.
Se exige ahora la familia carry por frases específicas («carry trade», «currency carry», «roll
yield»…). Cuarto bug del mismo tipo que los de subcadena — misma lección.

---

## (4) Mitigar el problema (A) — que E3 decida más veces

`estimate.extract_bruto_estimado` intenta, cuando no hay «Sharpe» directo, estimar el bruto de
OTRAS métricas del abstract: **information ratio** (≈ Sharpe), **retorno anual % / vol anual %**, y
**t-stat / √años**. Con eso E3 puede decidir en vez de mandar todo a `requiere_lectura`.

**Resultado honesto del retro-test: rescató 0 de los 80 candidatos de las corridas.** Los abstracts
de arXiv/Quantpedia no traen ret/vol, IR ni t-stat extraíbles por regex (igual que no traen
Sharpe). La mitigación EXISTE para candidatos futuros que sí reporten esas métricas, pero **no
resuelve el problema (A) para el material que hemos visto**: el cuello sigue siendo que los
abstracts no cuantifican, y el coste decide al LEER. Se reporta la fracción rescatada (0/80) en vez
de fingir que el filtro ahora ahorra sesión.

---

## (5) Retro-test sobre los 91 candidatos ya procesados (`scripts/e3_retro.py`)

Sin correr la run 003. Se re-evalúan los 80 candidatos de las corridas 001-002 con las reglas
nuevas (los 11 del backfill ya están a veredicto):

- **(B) Mueren en E3 con el factor de degradación: 1** — el **Sectoral Intramonth Momentum**
  (reportado 0.55 → efectivo 0.19 < requerido en ambos vehículos). **Muere en E3, no en el cribado
  aritmético posterior — exactamente lo previsto.** El único candidato que había pasado E3 en toda
  la historia viva ahora muere en E3, determinista y barato.
- **(A) Rescatados por métricas alternativas: 0/80** (ver arriba; honesto).
- **(C-D) Supervivientes de E3 tras la recalibración: 1** — la crypto mean-reversion
  (arxiv:2608.21888), `requiere_lectura` (no reporta bruto), familia **reversion**.
- **(E) Trabajo de sesión ahorrado:** E3 ahora decide **1 rechazo determinista** que antes llegaba
  a sesión y al cribado (antes: 0 rechazos en ambas corridas). Modesto —porque casi nada reportaba
  un Sharpe— pero real, y en la dirección correcta: el filtro empieza a morder.

---

## Conclusión

La recalibración hace lo que pedía: E3 ahora **descuenta** el bruto reportado (el Sectoral muere en
E3, no en el cribado), registra la **familia de riesgo** para vigilar la diversificación de las
CUATRO estrategias que hacen falta, y documenta que el listón es **0.4 neto POR estrategia** (0.4·√4
= 0.8). La mitigación de métricas alternativas existe pero no rescató nada del material visto — el
cuello sigue siendo que los abstracts no cuantifican. El factor 0.35 es **PROVISIONAL** con 3-4
puntos; se afina con cada candidato testeado. Con esto validado por el retro-test, la run 003 puede
correr con un E3 que muerde.
