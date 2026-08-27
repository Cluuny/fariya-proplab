# Veredicto del programa — CIERRE FORMAL (CFD y cripto)

**Versión FINAL y autosuficiente (2026-08-26, change program-close).** Este es el documento de
referencia del programa CERRADO. Cubre AMBOS ciclos —el universo CFD y el pivote a cripto/order
flow— con los números completos y sin adornos. Se consultará dentro de un año: **debe bastar por
sí solo.** El programa se REABRE únicamente si se cumple una de las tres condiciones OBJETIVAS de
`docs/reopening_conditions.md`, citando cuál y con el número — nunca por corazonada.

Dos ciclos, nueve familias con veredicto, **cero supervivientes**, y —medido de raíz— **ningún
terreno accesible con la AMPLITUD para generar un edge que despeje el listón** (§1.7-1.10). No es
un fracaso: es lo que produce un programa con falsadores honestos, suelo de costes medido, cribado
de amplitud, y veredictos sin adornos cuando el terreno no da un edge que supere el suelo.

## Las CINCO confirmaciones independientes del cierre

El cierre no descansa en un solo número: cinco medidas independientes, desde cinco ejes
distintos, dan el mismo veredicto — **lo requerido está por encima de lo alcanzable (0.32-0.37)**:

| eje | sección | requerido | alcanzable | veredicto |
|---|---|---|---|---|
| **Suelo de costes** | §1.2 | bruto **0.64** (CFD, net 0.40) | 0.37 trend / 0.495 carry (no desplegable) | no despeja |
| **Amplitud del terreno** | §1.7 | **N_eff ≥ 14** (para 0.50 a IC 0.05) | N_eff **8.15** (futuros, el más ancho) | no despeja |
| **Economía del payout** | §1.8 | bruto **0.50-0.80** (P(éxito) 50-80%) | 0.32-0.37 (≤ moneda al aire) | no despeja |
| **Volatilidad objetivo** | §1.9 | — (óptimo **8%**; EV ~$3.3k/año a 0.37) | subir vol INVIERTE el EV a negativo | no rescata |
| **Convergencia del pipeline** | §1.10 | ~4 supervivientes en familias distintas | **0 de 91**; tasa ~0 (cota 95% 3.3%) | no converge |

Cinco caras de **UNA** restricción estructural (§1.12): la amplitud efectiva del terreno accesible.
Y un hallazgo POSITIVO que, aun a favor, no la salva (§1.11): las estrategias SÍ se diversifican.

## Las nueve familias, con veredicto y números (1.1)

| familia | ciclo | veredicto | números clave |
|---|---|---|---|
| **H001** TSMOM (9 instr.) | CFD | **muerta** (falsada) | neto A 0.078 / B 0.135 (swap 0.3); bruto 0.24-0.31; el swap diario lo hundió |
| **H003** estacionalidad (TOM) | CFD | **muerta** (falsada) | efecto pooled −3.0 bps/día (IC cruza 0); Sharpe 0.26 = media del nulo (p 0.29) |
| **H007** TSMOM (17 ampliado) | CFD | **muerta** (falsada) | neto A 0.184 / B 0.040 (swap 0.3); **bruto A 0.370 — el mejor de trend**; marco UNDERPOWERED |
| **H002** carry (dif. tasas) | CFD | **rechazada** (concentración) | **neto 0.282 — el MEJOR del proyecto**; N_eff FX 3.41, casi todo short-JPY → prima de crash |
| **H005** reversión (índice) | CFD | **rechazada** (coste) | turnover 50-100×/año → bruto requerido ~0.78; plausible 0.3-0.5; cerrada sin correr |
| **H006** intermarket / macro | CFD | **rechazada** (coste) | price-based, duty 100% → requerido 0.64; sin evidencia de bruto alto (lead-lag decaído) |
| **COT** posicionamiento | CFD | **cribada** | Sharpe activo del fade ≈ 0 (agrupado −0.02, IC cruza 0); signo del mecanismo roto en 5/8 |
| **OFI** order flow | cripto | **cribada** | contemporáneo validado (R² 0.64) pero predictivo ~0; ratio señal/coste 0.009-0.039 (coste 25-100×) |
| **H008** subasta / volume profile (AMT) | cripto | **muerta** (falsada) | Sharpe activo del fade -0.067 ≪ listón 0.961 (con fills ≥5bps -0.986); niveles de perfil NO redundantes con simples (coincidencia 26%) pero la regla de subasta no da edge |

(H004 volatility risk premium quedó **fuera por datos** — necesita opciones/vol implícita —
sin llegar a veredicto de familia; no cuenta entre las familias con veredicto. La novena,
**H008**, entró por la vía que este mismo documento exige — salió del pipeline de investigación
(MP001, reabierta), no de una corazonada — se testeó y murió.)

## Las conclusiones MEDIDAS de ambos ciclos (1.2)

1. **Suelo de costes CFD: break-even 0.24, bruto requerido 0.64** (net > 0.40). Dominado
   por el margen diario (0.42 bp/día ≈ 1.96%/año, ~92% del coste). `docs/cost_floor.md`.
2. **El duty cycle bajo NO ayuda.** El requerido de serie completa baja con el duty, pero el
   alcanzable se diluye igual → el **Sharpe ACTIVO requerido SUBE**:
   `0.40/√duty + 0.245` = 1.14 a duty 20%, 1.51 a 10%. Ser selectivo no baja el coste del edge.
3. **Ninguna familia accesible produce el bruto requerido.** Los mejores: carry 0.495
   (bruto), trend 0.370 (H007-A) — ambos cortos de 0.64. La industria da 0.14 neto para
   trend en nuestra ventana (≈0.32 bruto de comisiones tras sumar el "2 y 20").
4. **Cripto: coste por unidad de riesgo favorable (0.013-0.032 vs 0.063 MES)** — BTC tiene
   ~3× la vol con comisiones ~1.6×. PERO el **listón absoluto en el mejor caso es 0.65**
   (maker + 1 rt/día + funding evitado), **idéntico al 0.64 del CFD** que mató seis familias.
   El vehículo cambia; el listón no.
5. **Market making imposible a VIP0:** comisión maker 2 pb vs spread medido 0.03 pb (≈65×).
   Ser maker sólo AHORRA comisión (5→2 pb), no genera ingreso; la señal debe producir
   >4 pb/round-trip sólo para empatar.
6. **El motor está validado externamente:** H001 neto 0.08-0.14 vs SG CTA Trend 0.14 en la
   misma ventana. No medimos de menos ni de más — reproducimos el número de la industria.
7. **Las restricciones son de DATOS y VEHÍCULO, no de MÉTODO.** El método mató lo que tenía
   que matar, el suelo cribó el resto, los veredictos fueron honestos (incluidas expectativas
   comprometidas refutadas: carry pasó el cribado que se esperaba que fallara; H007 salió
   underpowered).

   **Corrección de procedencia (D2, 2026-08-24, change provenance-corrections):** las
   expectativas de trend de H001 (0.40) y H007 (0.29-0.37) se anclaron en el Sharpe ~1.2 de
   Moskowitz-Ooi-Pedersen, que estaba MAL CITADO (está en Figure 2, no en texto; el período
   correcto es 1985-2009, no 1965-2009). Ese ancla defectuosa contamina el sesgo de
   calibración que se había reportado (+0.057): NO era evidencia limpia de que el marco
   Grinold-Kahn sobreestime. **Conclusión honesta: no hay calibración de expectativas
   todavía** — con dos anclas defectuosas y una corrida underpowered, la métrica empieza a
   existir sólo cuando el pipeline produzca corridas con ancla citable
   (`docs/extraction_defects.md`, reporte del pipeline). El VEREDICTO de las nueve NO cambia.

## Los dos hallazgos empíricos PROPIOS (1.3)

Mediciones originales sobre un mercado (cripto perp) con literatura pública escasa. No son
notas al pie: son resultados.

**a) ĉ ≈ 2.5-3.0 en cripto vs 0.45 del paper en acciones** (Cont-Kukanov-Stoikov). El
tamaño DISPLAY del mejor nivel sobreestima **~5-6×** la profundidad que realmente absorbe
flujo agresivo — liquidez fugaz / no comprometida. Es ESTABLE a 1s/2s/10s/30s (ĉ 2.5-2.7,
de 188 a 5621 eventos/bin) → no es un bug de unidades (las dimensiones cuadran, ĉ en ticks)
ni un artefacto de cancelación intra-bin (sería creciente con Δt). Va en dirección OPUESTA a
las acciones: en cripto los precios son MENOS resilientes que su book display, no más.

**b) El trade imbalance NO queda subsumido por el OFI en cripto** (t 6-9, significativo en
96-100% de submuestras) al contrario que en acciones (t cae ×4, significativo en 31%). La
formación de precios en cripto está más impulsada por TRADES que por QUOTES. Implicación
práctica: gran parte de la señal contemporánea vive en los aggTrades (archivos ~10× más
pequeños que el bookTicker).

## Los dos hallazgos limpios de H008 (1.3b)

De la novena familia (subasta / volume profile en BTC/ETH perp, 1094 días-instrumento):

**a) Los niveles de perfil NO son redundantes con niveles simples.** Coincidencia
26% [23,28] con emparejamiento y timescale correctos; POC vs VWAP mediana 32 bps. El
POC/VAH/VAL marca precios DISTINTOS de una banda de volatilidad o un VWAP. La expectativa
COMPROMETIDA de la ficha (coincidencia >60-80%, redundancia) queda **REFUTADA** — un
resultado limpio, no un fallo de ejecución.

**b) La regla de fade de subasta sobre esos niveles NO produce edge.** Distintos ≠ mejores:
el fade de extensiones hacia el POC da Sharpe activo -0.067 (con fills ≥5bps -0.986), muy
por debajo del listón 0.961, en 341 episodios / 18 meses / 2 instrumentos. En un mercado
momentum-driven, fadear la extensión pierde dinero. (El benchmark nulo original sugería que
"los niveles llevan información", pero era un test defectuoso — geometría rota, objetivo del
lado equivocado con entrada aleatoria — y se retiró del veredicto; ver `docs/h008_block4.md` D4.)

## Corrección metodológica del Bloque B (1.4)

Los "Sharpe implícito" de la tabla de decaimiento (hasta 462.9) **NO son creíbles como
NIVELES**: usan IR = IC·√BR con BR = 31.5M apuestas/año, y las apuestas a 1s están
fuertemente autocorrelacionadas (el propio paper: las autocorrelaciones del OFI se desvanecen
a ~10s). El VEREDICTO sobrevive porque el **RATIO señal/coste sí es informativo** — el mismo
BR inflado aparece en ambos lados: señal ∝ √BR, coste ∝ BR, ratio ∝ 1/√BR.

Ratios señal/coste con n fiable: **1s 0.022 · 5s 0.020 · 10s 0.009 · 30s 0.039 · 1min 0.025.**
Todos ≪ 1 (el coste supera la señal 25-100×). Consistencia verificada: de 1s a 30 min el
ratio mejora ×42, y √(86400/48) = 42.4 — exactamente el escalado 1/√BR esperado. **En
futuros reportes de cribado se usa el RATIO, no el nivel.**

## La condición de parada se cumplió (1.5)

Condición de parada del programa, textual:

> "Si tras probar las familias operables ninguna supera el suelo de costes con un bruto
> respaldado por la literatura, el programa se detiene: el cuello de botella no es de método
> sino de acceso a datos/vehículo, y no se busca una familia más por corazonada."

**Cumplida: 9 de 9 familias con veredicto, cero supervivientes.** Se declara cumplida y se
registra que **no se buscó ninguna familia por corazonada.** La novena (**H008**, subasta /
volume profile) NO fue una excepción a esta regla: entró exactamente por la vía que la regla
exige — salió del pipeline de investigación (MP001, reabierta con datos gratis de cripto), se
pre-registró con falsador y se testeó. Murió (Sharpe activo -0.067 ≪ 0.961). Cualquier
familia futura debe entrar por esa misma vía — nunca de una intuición.

## Validación externa de una conclusión propia (1.6)

El pipeline, en su corrida 002 (`docs/pipeline_run_002.md`), surfó un preprint independiente
que **valida desde fuera una CONCLUSIÓN del programa, no sólo el motor.** Hasta ahora la única
validación externa era del MOTOR (H001 neto 0.08-0.14 vs SG CTA Trend 0.14). Ésta es de una
CONCLUSIÓN:

**arxiv:2608.21888 (Short-horizon mean reversion in cryptocurrency markets, 2026)** mide, sobre
183 pares de Binance con protocolo estrictamente out-of-sample + holdout congelado de 6 meses,
un edge de reversión direccional a 15 min que **«peaks near 1.3 bp per trade against a 5 bp
round-trip cost: large enough to detect, too small to clear costs».** Es EL MISMO muro que el
programa encontró por su cuenta, en el MISMO mercado (cripto), dos veces:

- **OFI** (Cont-Kukanov-Stoikov en BTCUSDT): señal real pero minúscula, **ratio señal/coste
  0.009-0.039** (coste 25-100× la señal) → order flow cerrado.
- **H008** (subasta/volume profile): niveles informativos pero Sharpe activo del fade -0.067,
  sub-listón; la regla de subasta no netea.

Un grupo independiente, con datos y método propios, reporta la misma física: **en microestructura
de cripto hay señal contemporánea/de corto plazo real, pero el coste la supera.** No es una cita
que confirme nuestro código; es una réplica externa de nuestra CONCLUSIÓN de que el cuello es el
coste/vehículo, no la ausencia de señal. Primera de su tipo en el programa.

## El cierre por AMPLITUD del terreno (1.7)

Después de nueve familias muertas, muchas por amplitud, se hizo la pregunta que decide de una vez:
**¿cuál es el N_eff MÁXIMO alcanzable con universos que podemos operar Y pagar ($125/mes), y su
techo de IR supera el listón?** (`docs/terrain_breadth.md`, `scripts/terrain_breadth.py`; N_eff =
(Σλ)²/Σλ² de la matriz de correlación de retornos diarios).

**Respuesta MEDIDA: NO para todos.**

| universo | N_eff | $/mes | IR techo (IC .05) | vs listón 0.64 |
|---|---|---|---|---|
| Cripto perps 30 (Binance, GRATIS, acceso ilimitado) | **2.16** | 0 | 0.073 | NO (9×) |
| CFD Dukascopy 17 | 5.02 | ~0 | 0.112 | NO (6×) |
| ETFs sector/país/factor 25 | 3.31 | 0 | 0.091 | NO |
| **Futuros CME ~26 (el más ancho, proxy)** | **8.15** | ~50 | **0.143** | **NO (4.5×)** |
| combinaciones (cripto+CFD, futuros+cripto) | 4.36 / 5.83 | — | ≤0.12 | NO |

El universo con acceso ilimitado y gratis (cripto) es el PEOR: **N_eff 2.16, correlación mediana
0.68 — todo co-mueve con BTC, la cola de altcoins no añade dimensiones.** El más ancho accesible
(futuros, $50/mes) topa en un techo de IR de 0.14. Robusto a la frecuencia: incluso a rebalanceo
mensual con IC fuerte (0.05), el mejor llega a 0.49 < 0.64 (superar 0.64 exigiría N_eff ≥ 14, que
ningún universo accesible alcanza). **Las dos paredes se cierran juntas: a baja frecuencia falta
amplitud; a alta frecuencia sobra coste.**

Esto es MÁS FUNDAMENTAL que el suelo de costes: aunque la señal fuera perfecta (IC 0.05) y los
datos gratis, **la amplitud efectiva del terreno accesible es demasiado pequeña para un IR que
despeje el objetivo de 0.40 neto.** El cuello no es la señal ni el coste por separado — es que el
terreno no tiene suficientes apuestas independientes. **Por eso la run 003 del pipeline NO se
ejecutó: decirlo con el número es más informativo que cuatro corridas más.** (Caveat honesto: el
cierre es relativo al objetivo de 0.40 neto y a los IC bajos que el programa demostró; con la mitad
de ambición o un IC elite el cálculo cambiaría, pero ninguno está sobre la mesa.)

## La economía del payout — el cierre desde el lado del INGRESO (1.8)

`src/challenge.py` (el simulador de barrera de la semana 4) aplicado por primera vez al ciclo
completo de fondeo (`docs/funded_sharpe_requirement.md`). **El Sharpe BRUTO mínimo para pasar,
ganar y sobrevivir es ~0.5** (P(éxito)≥50%, moneda al aire) **a ~0.8** (70-80%, ingreso fiable),
donde P(éxito) = P(pasar ambas fases) × P(sobrevivir 12 ciclos). Lo desplegable —trend 0.37,
industria CTA 0.32— queda EN o por DEBAJO de la moneda al aire; el mejor que el programa midió,
H002 0.495, roza el 50% pero NO es desplegable (concentración, §1.12). **El negocio de fondeo
exige justo el Sharpe que el terreno no da** — la misma pared, vista desde el payout en vez del
suelo de costes. (Todos los caveats del modelo —supervivencia optimista, retornos normales—
empujan el requerido hacia ARRIBA.)

## La sensibilidad a la volatilidad objetivo (1.9)

Un hallazgo intermedio —P(quemar)≈0 en el barrido inicial— sugirió que quizá la restricción de
vol al 8% (§2.1 del documento maestro) estaba mal calibrada y una vol alta rendiría más sin que la
barrera mordiera. Se testeó (`docs/funded_vol_sensitivity.md`) y se REFUTÓ. El modelo normal
ingenuo dice que subir la vol mejora el valor esperado; al levantar los tres caveats
—supervivencia ACUMULATIVA (no independiente), retornos REALES con colas (curtosis ~3.2), y límite
diario INTRADÍA— la barrera muerde por encima de ~12% de vol (P(quemar 12): 15%→0.83, 20%→0.97) y
el EV se INVIERTE a negativo. **El óptimo sigue siendo ~8% (EV ~$3.3k/año a Sharpe 0.37 sobre una
cuenta de 300k que hay que alcanzar) → la restricción de §2.1 queda VINDICADA.**

**Autocorrección registrada:** el P(quemar)≈0 era un ARTEFACTO DOBLE (sólo se barrió vol ≤10% Y se
usó supervivencia independiente, ambas optimistas). El análisis de volatilidad, con la supervivencia
acumulativa, lo refutó — la barrera muerde ya a 8% (~0.15-0.22). Es un ejemplo de que el sistema
CORRIGE SUS PROPIAS CONCLUSIONES: una lectura provisional se marcó, se testeó y se retractó con el
número, igual que el nulo defectuoso de H008 o la coincidencia mal emparejada.

## El pipeline de búsqueda no puede converger (1.10)

La quinta confirmación no es sobre una estrategia sino sobre la BÚSQUEDA misma. El pipeline de
investigación procesó **91 candidatos ciegos** (`docs/pipeline_run_001.md`, `_002.md`) con
**0 supervivientes** a una estrategia viable. Con 0 éxitos en 91, el estimador puntual de la tasa
de éxito es **0**; la cota superior al 95% (regla de tres) es ~3/91 ≈ **3.3%**. Aun en ese caso
optimista, harían falta **~120 candidatos para UN superviviente esperado**, y **~4× eso más la
restricción de que caigan en cuatro FAMILIAS DISTINTAS** — del orden de varios cientos. Con el
estimador puntual (0), **NINGÚN N finito da supervivientes esperados.**

**La condición de parada de 200 estaba infradimensionada** para el objetivo de cuatro
supervivientes en familias distintas — pero es moot: no es que falten candidatos, es que la tasa de
supervivencia es ~0 porque falta amplitud DENTRO de cada familia (§1.7). El pipeline funciona y está
limpio (cinco defectos hallados y corregidos, un adversario de once ejes, un cribado de costes que
muerde); lo que no converge es la búsqueda, porque el terreno no contiene el objeto que busca.
**El programa se cierra por TASA, no por agotamiento de la cuota.**

## El hallazgo estructural POSITIVO — las estrategias sí se diversifican (1.11)

Un resultado MEDIDO que va A FAVOR del plan, y que aun así no lo salva — por eso merece registrarse
con precisión (`docs/pre_run_003_calibration.md`, `scripts/family_breadth.py`). Se midieron las
series de retorno diario neto de tres familias (trend, carry, estacionalidad) con el motor real
sobre 2011-2026:

| | trend | carry | estacionalidad |
|---|---|---|---|
| trend | 1.00 | 0.08 | 0.05 |
| carry | 0.08 | 1.00 | 0.13 |
| estacionalidad | 0.05 | 0.13 | 1.00 |

Correlación media **0.09** → **N_eff de ESTRATEGIAS = 2.95** (de 3; el ideal), extrapolado a 4
familias **3.91**. **A diferencia de los INSTRUMENTOS** —que correlacionan 0.7-0.8 y colapsan el
N_eff a 2-8 (§1.7)— **las ESTRATEGIAS son casi ORTOGONALES.** Combinar familias multiplica el BR
como predice la teoría (0.4·√4 ≈ 0.8; con el N_eff medido, el Sharpe individual necesario es
0.40-0.47, apenas por encima del 0.40 asumido). **El temido ρ=0.6 entre trend y carry no se
materializó: es 0.08.**

**EL CUELLO NUNCA FUE COMBINAR. FUE PRODUCIR LA PRIMERA.** El plan de cuatro estrategias
descorrelacionadas es estructuralmente correcto —la diversificación por familia es real y medida—
pero se apoya en tener CUATRO familias cada una a 0.40 neto, y el terreno no produce ni UNA
(§1.7-1.10). Un motor de multiplicación de BR perfecto, sin nada que multiplicar.

## La relectura — una restricción, nueve veces (1.12)

Con el cierre por amplitud (§1.7) en la mano, las nueve muertes se leen distinto de como se
leyeron en su momento. **Al menos 5 de las 9 no murieron por lo que creímos entonces (coste,
concentración, redundancia, efecto inexistente): murieron por AMPLITUD** — el terreno no tenía
suficientes apuestas independientes para que ninguna señal despejara el listón.

| familia | causa que le pusimos entonces | N_eff real | relectura |
|---|---|---|---|
| **H001** trend (9 instr) | coste (swap diario) | **3.73** | amplitud: 9 CFD macro ≈ 3.7 apuestas |
| **H007** trend (17 instr) | coste / underpowered | **5.32** | DUPLICAR instrumentos sólo llevó N_eff a 5.3 — sigue corto |
| **H002** carry (FX) | concentración (short-JPY) | **3.41** | «concentración» ES amplitud: N_eff 3.41, casi todo una apuesta |
| **candidato sectorial** | sobreajuste (backtest) | **1.29** | 9 sectores a ρ0.75 = 1.3 apuestas; irresoluble por amplitud |
| **H008** volume profile | regla de subasta sin edge | **~1.1** | 2 instrumentos a ρ0.8 → N_eff efectivo del par ~1.1 |
| **OFI** order flow | coste (ratio 0.009-0.039) | bajo | además del coste, 1 instrumento; y cripto entero es N_eff 2.16 |

Las otras (H003 estacionalidad = beta; H005/H006 = coste; COT = efecto inexistente) murieron
por su razón propia, pero ninguna tenía amplitud para compensar. **No fueron nueve fracasos
independientes: fue UNA restricción estructural — la amplitud efectiva del terreno accesible —
manifestándose nueve veces con nombres distintos.** El cribado de amplitud (§1.7) la nombró de
frente: el mejor universo accesible topa en N_eff ~8 (futuros, $50/mes) y el gratis/ilimitado
(cripto) en 2.16. Cada familia chocó con la misma pared por un lado distinto.

Esto no invalida ningún veredicto (cada uno fue correcto en sus términos) — lo UNIFICA. El
programa no necesitaba una décima familia; necesitaba amplitud que el terreno no tiene.

## Cierre

Dos ciclos, dos vehículos (CFD spot y cripto perp), nueve familias, cero edge que supere el
suelo — y, medido de raíz, **ningún terreno accesible con la amplitud para generarlo** (§1.7),
confirmado desde CUATRO ejes independientes (coste §1.2, amplitud §1.7, payout §1.8, vol §1.9),
que en la relectura (§1.12) resulta ser la MISMA restricción tras al menos 5 de las 9 muertes. El
programa convirtió "¿funciona X?" en números falsables y mató cada idea por la razón correcta antes
de arriesgar capital, y finalmente midió que el límite no era una idea más sino la AMPLITUD del
terreno al que se tiene acceso. Lo que sigue no es otra familia ni otra corrida: es medir la
degradación backtest-vs-vivo con capital propio (`docs/own_capital_phase.md`), una fase de
INSTRUMENTACIÓN, no de ingreso.
