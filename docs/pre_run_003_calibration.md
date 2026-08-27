# Dos calibraciones antes de la run 003

**Fecha:** 2026-08-27. **Modo:** aritmética + una medición con datos propios; sin correr la run
003. Ambas cambian el sentido de gastar 4-5 sesiones en las corridas 003-006.

---

## (1) Calibrar el factor de degradación con más puntos

`FACTOR_DEGRADACION = 0.35` gobierna todo el filtro E3 (define el umbral de bruto reportado). Tenía
3 puntos propios. Ampliación de la base de calibración:

**Intento con Quantpedia — NO obtenible del tier gratuito.** El screener libre
(`quantpedia.com/screener/`) expone `paperSharpeRatio` sólo como **filtro agregado** (buckets:
«0-0.5», «0.5-1», …), NO el Sharpe REALIZADO de su implementación por estrategia. El campo
realizado/OOS por estrategia es premium. No hay forma de sacar 15-25 pares (reportado, realizado)
limpios del tier gratuito. **Sesgo obvio si los tuviéramos:** Quantpedia elige qué implementar →
su muestra sobre-representa lo que REPLICÓ → el ratio saldría sesgado HACIA ARRIBA (E3 demasiado
laxo). No se usa.

**Base de calibración honesta (literatura arbitrada + puntos propios):**

| fuente | ratio reportado→realizado | n | nota |
|---|---|---|---|
| **Nuestros** (TSMOM 1.2→0.37 · TOM →0 · Sectoral 0.55→~0.4) | **0.31 · ~0 · ~0.7 (media 0.35)** | 3 | mismo motor y costes → los MÁS relevantes |
| McLean & Pontiff 2016 (JF), 97 predictores | **0.74** (post-muestra, sesgo in-sample) / **0.42** (post-publicación, +arbitraje) | 97 | equity cross-sectional (no operable por nosotros) |
| Chen & Zimmermann 2022 (open-source AP) | **~0.5** (t-stats OOS/IS, la mayoría replica más débil) | ~200 | equity cross-sectional |

**Distribución del ratio:** rango ~0 a ~0.74; mediana de la literatura de equity **~0.42-0.5**;
nuestra media propia **0.35**. **0.35 está dentro del rango plausible — en el extremo CONSERVADOR**
(por debajo de la mediana de equity). Es el lado seguro para un filtro cuyo trabajo es NO gastar
sesión en falsas esperanzas, y está anclado en nuestro realizado (el más pertinente: nuestras
familias operables —trend/carry/macro— y nuestro suelo de costes, no anomalías de equity).

**Decisión: se mantiene 0.35 (PROVISIONAL), y NO se re-corre el retro-test — porque el resultado es
INSENSIBLE al factor en todo el rango plausible.** Un candidato sobrevive E3 (futuros) si
`reportado > 0.42/factor`; ese umbral va de 1.20 (factor 0.35) a 0.57 (factor 0.74). **El Sectoral
(0.55) queda por debajo del umbral para CUALQUIER factor ≤ 0.76** → muere en E3 en todo el rango; y
los otros 90 no reportan número. **El valor exacto del factor es inmaterial para los 91 ya
procesados;** sólo importará para futuros candidatos que reporten un Sharpe en la banda sensible
(~0.57-1.20 según el factor). Se refina con cada candidato testeado (el registro de aprendizaje
guarda reportado vs medido); con datos propios nuevos el factor migra.

---

## (2) ¿Existe la diversificación por familia? — MEDIDO

Todo el plan se apoya en **0.4 · √4 = 0.8**, y ese √4 exige cuatro estrategias DESCORRELACIONADAS,
lo que nunca se había medido. Se generaron las series de retorno diario NETO de tres familias con
el motor real (`scripts/family_breadth.py`) y se midió su correlación sobre la ventana común
**2011-09→2026-08 (3742 días)**:

- **trend** (`signals.tsmom`, 17 instr): Sharpe neto +0.13
- **carry** (proxy: signo del diferencial de tasas histórico × inverse-vol; H002 se cribó sin señal): +0.38
- **estacionalidad** (`signals.tom_seasonal`, índices): +0.19

**Matriz de correlación (retornos diarios netos):**

| | trend | carry | estacionalidad |
|---|---|---|---|
| trend | 1.00 | 0.08 | 0.05 |
| carry | 0.08 | 1.00 | 0.13 |
| estacionalidad | 0.05 | 0.13 | 1.00 |

- **Correlación par a par: trend-carry +0.08 · trend-estacionalidad +0.05 · carry-estacionalidad +0.13** (media **+0.09**).
- **N_eff de ESTRATEGIAS = 2.95** (de 3 familias; el ideal es 3). Multiplicador real **√N_eff = 1.72**, prácticamente **√3 = 1.73**.
- Extrapolado a 4 familias a esa misma correlación media (participation ratio) → **N_eff ≈ 3.91**.

**La diversificación por familia EXISTE, y es casi perfecta.** A diferencia de los INSTRUMENTOS
(que correlacionan ~0.7-0.8 en cripto/CFD y colapsan el N_eff a 2-8), las ESTRATEGIAS son casi
ortogonales (ρ ~0.09). **Es la última fuente de amplitud que el terreno no agota, y está verificada
en positivo.** El temor del bloque —que trend y carry correlacionaran ~0.6, subiendo el Sharpe
requerido a 0.5— NO se materializa: correlacionan 0.08.

**Sharpe individual necesario para 0.8:**

| escenario | N_eff | Sharpe individual = 0.8/√N_eff |
|---|---|---|
| 3 familias medidas | 2.95 | **0.47** |
| 4 familias a ρ=0.09 (extrapolado) | 3.91 | **0.40** |

Con CUATRO familias casi-descorrelacionadas, **0.40 por estrategia ≈ es correcto** (la suposición
del plan se sostiene). Con sólo TRES haría falta 0.47.

---

## (3) Decisión sobre la run 003

**Con los dos números:**
- **Umbral de bruto reportado final** (E3, factor 0.35 sin cambio): **~1.20 (futuros) / ~1.83 (CFD)**.
- **Sharpe individual necesario dado el N_eff de estrategias real:** **0.40-0.47 neto** por
  estrategia (0.40 con 4 familias, 0.47 con 3) — apenas por encima del 0.40 asumido, porque la
  diversificación es casi perfecta. Esto sube el umbral de E3 sólo marginalmente (el requerido pasa
  de basarse en 0.40 a ~0.40-0.47 neto; en bruto reportado, de ~1.20 a ~1.35-1.40 en futuros).
- **Cuántos de los 91 sobrevivirían:** **0 a una estrategia viable** (1 queda en `requiere_lectura`
  —la crypto mean-reversion, familia reversion— y está pre-refutada por su propio edge 1.3bp<5bp).

**¿Cuántos candidatos para esperar CUATRO supervivientes en familias distintas?** Con la tasa
observada de **0 de 91**, el estimador puntual de la tasa de éxito es **0**. La cota superior al 95%
(regla de tres, 0 éxitos en 91) es ~3/91 ≈ **3.3%**; incluso en ese caso optimista harían falta
~**120+** candidatos para UN superviviente esperado, y **~4× eso más la restricción de que caigan en
4 familias DISTINTAS** — del orden de varios cientos, en el mejor caso. Con el estimador puntual (0),
NINGÚN N finito da supervivientes esperados. **Conclusión: a la tasa observada, 200 NO alcanza para
esperar cuatro supervivientes en familias distintas; la condición de parada de 200 estaba
infradimensionada para ese objetivo.** Pero es MOOT: el programa ya cerró por AMPLITUD
(`docs/terrain_breadth.md`) — el terreno no rinde supervivientes por-familia a ningún N, no porque
falten candidatos sino porque falta breadth DENTRO de cada familia. Correr 003-006 procesaría ~160
candidatos más para, en expectativa, cero supervivientes.

**Veredicto: NO correr la run 003.** Las dos calibraciones lo confirman desde ángulos opuestos: la
diversificación por familia SÍ existe (buena noticia estructural), pero la tasa de supervivencia por
familia es ~0 y ningún universo accesible tiene la amplitud INTRA-familia para generar el 0.40 neto
que cada una necesitaría (§1.7 del veredicto). El cuello nunca fue combinar familias —eso funciona—
sino producir UNA sola que despeje el suelo, y el terreno no la da.
