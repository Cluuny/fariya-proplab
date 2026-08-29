# Cribado de amplitud y prima de volatilidad en cripto (Deribit)

**Fecha:** 2026-08-29 (calendario del proyecto; datos de mercado REALES hasta ~2025-08). **Modo:**
CRIBADO, no hipótesis (como COT/H002/OFI): no consume intentos, no requiere ficha, no toca holdout.
Fuente: `scripts/crypto_vol_screen.py` sobre la API pública gratuita de Deribit (+ Binance para el
spot). **VEREDICTO: INDETERMINADO, con sesgo a NO despejar** — la primera vez en el programa que la
expectativa comprometida no descarta de entrada, y aun así ninguna lectura da IR>0.65 **con margen**.

## D1 — Cobertura de datos (Bloque 1.1, verificado ANTES de construir)

| serie | disponible gratis | fuente |
|---|---|---|
| **DVOL** (índice de vol implícita ~30d ATM), BTC/ETH, diario | **SÍ**, ~2021→2025-08 (cap 1000 pts/llamada → ventana usada 2022-12→2025-08) | `get_volatility_index_data` |
| OHLC del perp (para vol realizada) | SÍ | `get_tradingview_chart_data BTC-PERPETUAL` |
| **prima IV−RV** (30d) | SÍ (construible de lo anterior) | derivada |
| ATM 7d/90d, **pendiente de estructura temporal**, **skew 25-delta** | **NO** | `get_instruments?expired=true` sólo retiene ~semanas de opciones vencidas → la cadena histórica no es reconstruible gratis |

**Limitación honesta:** sólo se construye la prima IV−RV (30d), que es el NÚCLEO de la prima de
volatilidad, pero no la superficie completa (skew, estructura temporal). **La amplitud medida es una
COTA INFERIOR:** las series de skew/estructura que faltan son justo las que añadirían dimensiones
ortogonales. Calidad: sin huecos >25%, DVOL y perp continuos en la ventana.

## D2 — Amplitud (participation ratio, mismo cálculo que `terrain_breadth.py`)

| universo | N_eff | nota |
|---|---|---|
| a) spot cripto 30 solo | **2.16** | referencia (coincide con terrain_breadth) |
| c) series de vol solas (IV/RV/PREM × BTC/ETH, 6 series) | 3.88 | entre ellas hay algo de diversidad |
| **b) spot + vol combinado (36 series)** | **3.08** | lo que realmente operarías |

**Aporte marginal por serie ≈ +0.18-0.19 cada una; la vol añade en total +0.92 (2.16 → 3.08).**
Está **por DEBAJO de la expectativa comprometida (4-5)**. Dos razones honestas: (1) sólo tengo
DVOL-based (no la superficie completa que añadiría más dimensiones ortogonales); (2) el test de
constructibilidad de `docs/breadth-lessons.md` NO separó limpiamente aquí — la vol realizada (RV,
derivable del spot) aportó lo MISMO que la implícita (~0.18), porque medí cambios DIARIOS de un
estadístico rodante de 30d (la RV cambia lento, su cambio diario no es función instantánea del spot).
Es un artefacto de medición para series de vol, no la señal limpia de EURCHF (+0.51) vs AUDJPY (+0.05).
**N_eff combinado = 3.08 (≈ dobla el spot pero lejos de 14).**

## D3 — IC de la prima de volatilidad (+ colas)

Señal = `zscore(IV_30d − RV_30d backward)`, conocida en t. **DOS aproximaciones del objetivo, y su
contraste ES el hallazgo:**

| objetivo | IC (no-solapado, n=63 indep) | IC95 (bootstrap bloque) | skew | curtosis(exc) |
|---|---|---|---|---|
| **(A) carry realizado** = IV_t − RV_realizada[t,t+30] | **+0.14** | [−0.008, +0.354] (cruza 0) | −0.87 | +0.66 |
| **(B) timing** = −(IV_{t+30}−IV_t) | **+0.03** | [−0.092, +0.153] (cruza 0) | −0.57 | +1.41 |

**El «IC alto» (0.14) es en su mayoría MECÁNICO:** la señal (IV−RV_back) y el objetivo-A
(IV−RV_fwd) COMPARTEN el nivel IV_t, así que un régimen de IV alta auto-correlaciona ambos. Con el
objetivo LIMPIO (cambio de IV, que no comparte nivel), el IC de TIMING colapsa a **~0.03**. Además el
IC del carry, con su propia IC95 [−0.008, +0.354], **cruza 0 → ni siquiera es significativamente
positivo.** Observaciones independientes: sólo **63** (vencimientos solapados a 30d, no 365/año).

**CAVEAT DE COLA (obligatorio):** el retorno short-vol tiene **skew NEGATIVA (−0.6 a −0.9) → cola
IZQUIERDA** — gana poco muchas veces y pierde de golpe en los picos de vol. Un IC positivo con cola
izquierda gorda NO es un IC limpio: la prima existe como compensación por ese riesgo de cola, no
como alfa gratis.

## D4 — IR alcanzable vs listón 0.65 (Bloque 4)

`IR = IC × √(12 × N_eff_combinado)`, con N_eff_comb = 3.08 → multiplicador √(12·3.08) = 6.08:

| lectura | IR punto | banda (IC95) | veredicto |
|---|---|---|---|
| (A) carry (inflado por el nivel) | **0.85** | [−0.05, +2.15] | **INDETERMINADO** (cruza 0.65) |
| (B) timing (limpio) | **0.20** | [−0.56, +0.93] | **INDETERMINADO** (cruza 0.65) |

**VEREDICTO: INDETERMINADO, con sesgo a NO despejar.** El punto bajo la lectura más favorable (carry,
0.85) roza por encima de 0.65 — **la primera vez en nueve familias que un punto estimado toca el
listón** — pero: (1) ese IC está inflado mecánicamente por el nivel de IV; (2) su propia IC95 cruza 0
(no es significativamente positivo); (3) el IC de timing limpio es ~0 → IR 0.20; (4) N_eff aportó
3.08, bajo la expectativa 4-5; (5) la cola es izquierda (skew −0.6 a −0.9); (6) el multiplicador usa
el N_eff del LIBRO COMBINADO (generoso) — la prima sola opera BTC+ETH vol (N_eff ~1.5), que daría un
IR standalone menor. **Ninguna lectura da IR>0.65 CON MARGEN.** No se pre-registra (el criterio de
promoción era «IR>0.65 con margen», no un punto marginal con banda que cruza).

**Reapertura (C2, IC≥0.10):** el carry IC 0.14 podría parecer que roza el umbral C2 de
`docs/reopening_conditions.md`, pero su IC95 baja a −0.008 (cruza 0, no ≥0.10) y está inflado por el
nivel; el IC limpio es 0.03. **No cumple C2.** La puerta sigue cerrada por evidencia.

## D5 — Expectativa comprometida: ¿cumplida o refutada?

Escrita antes de correr: *N_eff combinado 4-5; IC de la prima 0.05-0.12; IR 0.37-0.93; resultado más
probable INDETERMINADO o marginalmente por encima; primera vez que la expectativa no descarta de
entrada.*

| parámetro | comprometido | medido | ¿cumplido? |
|---|---|---|---|
| N_eff combinado | 4-5 | **3.08** | **REFUTADO (más bajo)** — parte por la superficie no construible gratis |
| IC de la prima | 0.05-0.12 | carry 0.14 (inflado) / timing 0.03 | cruza el rango; el limpio queda por debajo |
| IR | 0.37-0.93, prob. indeterminado o marginal | 0.20 (timing) a 0.85 (carry), INDETERMINADO | **CUMPLIDO en su predicción central** |
| «no descarta de entrada» | sí | sí (punto carry roza 0.65) | **CUMPLIDO** |

**La expectativa se cumple en lo central (indeterminado, punto marginal bajo la lectura favorable) y
se refuta en la amplitud (3.08 < 4-5).** Es, honestamente, el resultado menos-negativo del programa:
la única clase de datos accesible cuyo punto estimado toca el listón. Pero no despeja con margen, la
señal limpia es ~0, la cola es izquierda, y —Bloque 5— el suelo de costes de opciones no está medido.

## Bloque 5 — Advertencia de ejecución (documentada, sin resolver)

Aunque el IC despejara, operar OPCIONES tiene un suelo de costes DISTINTO al modelado en
`costs_model.py`: **spreads anchos, liquidez concentrada en pocos strikes, y el riesgo de cola
asimétrico** (D3). El programa modela costes de perps (maker/taker + funding), no de opciones. **Ese
suelo habría que MEDIRLO aparte ANTES de cualquier pre-registro:** un IC que despeja con costes de
perps no despeja necesariamente con costes de opciones — y una prima delgada (carry ~IV−RV) es
justamente lo que un spread ancho se come. Con la prima marginal y la cola izquierda medidas, es
plausible que el suelo de costes de opciones cierre lo que el IC deja indeterminado.

## Conclusión

La superficie de vol implícita cripto —la última clase de datos accesible sin tocar— queda MEDIDA. La
prima de volatilidad existe como carry pero (a) su timing es ~0, (b) su IC significativo desaparece
al quitar la inflación mecánica, (c) aporta menos amplitud de la esperada (N_eff 3.08), (d) tiene cola
izquierda, y (e) su suelo de costes real (opciones) no está medido y probablemente la cierra.
**INDETERMINADO con sesgo a NO** — no se pre-registra, no se reabre H004 a hipótesis, y la puerta
sigue cerrada por evidencia, ahora también en volatilidad implícita. Para resolver el indeterminado
harían falta: la superficie histórica completa (no gratis en Deribit) y el suelo de costes de opciones
medido.
