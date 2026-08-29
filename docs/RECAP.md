# PropLab — RECAP / auditoría del programa

Documento definitivo de qué se hizo, cómo, y qué se midió. Autosuficiente: se lee entero de una
sentada y se entiende el programa sin abrir el código. **No es un resumen ejecutivo — es una
AUDITORÍA:** cada afirmación lleva su número y su ruta `archivo:línea` para poder verificarla.
Estado: **CERRADO**, tag `v1.2-closed`. Veredicto completo: `docs/program_verdict.md`.

**La tesis en una frase.** Un programa que convirtió «¿funciona X?» en números falsables y mató
cada idea por la razón correcta antes de arriesgar capital: **dos ciclos (CFD y cripto), nueve
familias, cero supervivientes**, y —medido de raíz— **ningún terreno accesible con la amplitud para
generar un edge que supere el suelo de costes**. Cinco cierres independientes convergen en el mismo
número: lo requerido (0.5-0.8 bruto / N_eff≥14) está por encima de lo alcanzable (0.32-0.37 /
N_eff 8.15).

---

## (1) Cronología — qué se construyó, en qué orden, y qué reveló

| bloque | qué se construyó | problema que resolvía | qué reveló al construirlo |
|---|---|---|---|
| **Motor** (`src/engine.py`, `loaders.py`, `signals.py`) | ingesta→limpieza→señales puras→retornos netos con costes | un solo punto de coste, señales sin I/O | **barra de domingo** (Dukascopy trae domingo; se filtra a Lun-Vie, el gap del finde se captura Vie→Lun close-to-close, `loaders.py:126`); **retorno cruzado de hueco** (con 9 instrumentos en 3 calendarios, `pct_change().fillna(0)` perdía el retorno real del gap → `_asset_returns` gap-safe, `engine.py:21-31`); vol gap-safe (`engine.rolling_vol:120`) |
| **Simulador de barrera** (`src/challenge.py`) | P(pasar el challenge) como problema de primer paso, block bootstrap | valorar el challenge, no la estrategia | **hardening: se retiró un valor por-año provisional mal especificado + un knob oculto**, y se añadió el guard de horizonte insuficiente (`p_unresolved>5% → nan`, `challenge.py:60-73, 244-247`); verificado contra fórmula cerrada (`analytic_pass_probability:368`) |
| **Familias CFD** (H001/H002/H003/H005/H006/H007, COT) | tsmom, tom_seasonal, carry, screening de costes | probar las seis familias operables del universo CFD | el **suelo de costes** mata la mayoría por aritmética antes de correr; el ancla de calibración estaba mal citada (§6) |
| **Modelo de costes** (`src/costs_model.py`) | suelo de costes como herramienta de decisión | ¿qué bruto hace falta para netear 0.40? | margen diario = **92%** del coste; el duty bajo SUBE el listón activo |
| **Pivote a cripto** (`src/crypto/`) | ingesta Binance, OFI, modelo de costes cripto, H008 | terreno investigable a coste cero | ĉ≈2.5-3.0 (§5); trade imbalance no subsumido; order flow predictivo ~0 |
| **Pipeline de investigación** (`src/pipeline/`) | descubrir→operabilidad→estrategia→costes→extraer→adversario→compuerta | arreglar la dependencia de fuente única (9 familias de un solo reviewer) | **tres/cuatro bugs de subcadena**: `ict`⊂`predict` (`triage_operability`), `carry`⊂`carrying`, `long the`⊂`along the`, y `carry` VERBO ⊂ mean-reversion (`estimate`) → todos corregidos con límite de palabra (`_hits_word`, `triage_operability.py`, `estimate.py`; test `tests/test_pipeline_word_boundary.py`) |
| **Fases de fondeo** (scripts/docs) | Sharpe requerido del ciclo, sensibilidad a la vol | ¿qué Sharpe hace falta para pasar-ganar-sobrevivir? | P(quemar)≈0 era artefacto doble (§6); el óptimo de vol es 8% |

---

## (2) Las nueve familias

Cada una: señal · mecanismo (quién perdía del otro lado) · universo/período · qué se midió · por
qué murió con el número · expectativa comprometida · **causa REAL tras la relectura** (§1.10 del
veredicto: al menos 5 de 9 murieron por AMPLITUD, no por lo que se creyó).

**H001 — TSMOM (trend).** El signo del retorno a 12 meses predice el del mes siguiente. Contraparte:
hedgers comerciales que pagan prima por transferir riesgo (+ subreacción conductual). 9 instrumentos
CFD spot, ~2011-2026, diaria. Bruto 0.24-0.31; **neto A 0.078 / B 0.135** (swap 0.3) → **muerta**
(falsada, <0.2). Expectativa 0.40 (Grinold-Kahn) — refutada (y el ancla estaba mal citada, §6).
**Causa real: AMPLITUD — 9 CFD macro = N_eff 3.73.**

**H007 — TSMOM ampliado (trend).** Igual, 17 instrumentos. Bruto A **0.370 (el mejor de trend)**;
neto A 0.184 / B 0.040 → **muerta**. Expectativa 0.29-0.37; el marco salió **UNDERPOWERED** (H007−H001
a ~1 SE, indistinguible de ruido). **Causa real: DUPLICAR instrumentos sólo llevó N_eff a 5.32.**

**H002 — Carry (dif. de tasas).** Long divisas de alto rendimiento, short las de bajo. Contraparte:
quien paga por evitar el riesgo de crash. FX majors. Bruto **0.495**, **neto 0.282 — el MEJOR del
proyecto**. NO murió por el listón: **rechazada por CONCENTRACIÓN** (N_eff FX **3.41**, casi todo
short-JPY → no es cartera, es una apuesta de prima de crash). Expectativa: se esperaba que FALLARA el
cribado → **refutada** (pasó). **Causa real: AMPLITUD (N_eff 3.41).**

**H003 — Estacionalidad turn-of-the-month.** Comprar el índice en la ventana [-1,+3] del cambio de
mes. Contraparte: flujos de calendario (nómina, rebalanceo). 3 índices, 2011-2023, diaria. Efecto
pooled **−3.0 bps/día (IC cruza 0)**; Sharpe 0.26 = **media del nulo** (p95 0.52, p 0.29) → **muerta**
(el exceso sobre el nulo ≈ 0). Expectativa: exceso ~0 sobre beta — confirmada la nulidad. **Causa
real: el Sharpe ERA el beta del mercado (§6, lección benchmark-cero); y baja amplitud.** Holdout NO
tocado (no pasó in-sample).

**H005 — Reversión a la media (índice).** Fade de desviaciones. 4 índices. **Cerrada SIN correr por
COSTE**: turnover 50-100×/año → bruto requerido ~**0.78**; plausible 0.3-0.5. Expectativa: no despeja
→ confirmada. Causa: coste (turnover) — que es amplitud temporal insuficiente para el turnover.

**H006 — Intermarket / macro (lead-lag).** Difusión de información entre mercados. 6 instrumentos.
**Cerrada SIN correr por COSTE**: duty ~100% → requerido **0.64**; sin evidencia de bruto alto
(lead-lag decaído). Causa: coste + señal decaída.

**COT — Fade de posicionamiento (no-precio).** Contra el posicionamiento extremo del COT. 8
instrumentos. **Cribada-fuera**: Sharpe activo del fade **≈ 0** (agrupado −0.02, IC cruza 0), signo
del mecanismo roto en **5/8**. Expectativa: señal débil — confirmada (dio cero exacto).

**OFI — Order Flow Imbalance (cripto).** Presión de flujo en el mejor nivel (Cont-Kukanov-Stoikov).
BTCUSDT perp, 4 días de regímenes. Contemporáneo **validado (R² 0.64)** pero **predictivo ~0**; ratio
señal/coste **0.009-0.039** (coste 25-100× la señal) → **cribada** (order flow cerrado). Expectativa
(B.5): confirmada. **Causa real: coste + 1 instrumento (cripto entero es N_eff 2.16).**

**H008 — AMT / Volume Profile (cripto).** Fade de extensiones fuera del value area hacia el POC.
BTC+ETH perp, 18 meses, duty real 0.31. Sharpe activo del fade **−0.067 ≪ listón 0.961** (con fills
≥5bps −0.986) → **muerta**. Niveles de perfil NO redundantes con simples (coincidencia 26%, POC vs
VWAP 32bps) pero la regla de subasta no da edge. Expectativa (muerta-por-redundancia o underpowered):
cumplida en dirección. **Causa real: 2 instrumentos a ρ0.8 → N_eff efectivo ~1.1;** murió por la
regla de subasta, no por redundancia.

**La relectura:** H001 (3.73), H007 (5.32), H002 (3.41), el candidato sectorial (1.29), H008 (~1.1),
OFI (1 instr) — **al menos cinco murieron por AMPLITUD, no por lo que se creyó en el momento (coste,
concentración, redundancia). Fue UNA restricción estructural con nueve caras.**

---

## (3) Los cinco cierres independientes — recalculables a mano

### 1. Suelo de costes (`costs_model.py`, `docs/cost_floor.md`)

Coste anual (fracción de NAV): `margin = swap_margin_daily · gross · trading_days` +
`spread = (spread+slippage) · turnover` − `carry` (`annual_cost`, `costs_model.py:36`). Verificado
(`costs_model.py:8-13`): gross 1.71, turnover 8.8 → margin **1.96%** + spread 0.13% − carry 0.19% ≈
**1.9%** de coste vs ~2.16% de bruto a 8% vol → Sharpe neto ~0.03. **El margen es ~92% del coste.**

Bruto requerido para netear 0.40: `requerido = breakeven_full·duty + umbral` (`sharpe_bruto_requerido_duty`,
`costs_model.py:105`). CFD: `breakeven_full=0.24` (margen diario, `BREAKEVEN_FULL_DUTY:68`) → a duty
1.0, **0.24·1 + 0.40 = 0.64**. Futuros: `0.024` (sin margen diario) → **0.024 + 0.40 ≈ 0.42**.

- **El gross NO es palanca:** el margen escala con el gross, así que subir exposición sube coste y
  bruto requerido en la misma proporción — Sharpe invariante.
- **El duty bajo SUBE el listón activo:** `sharpe_activo_requerido = 0.40/√duty + 0.245`
  (`costs_model.py:121`) = **1.14 a duty 20%, 1.51 a 10%**. Ser selectivo no baja el coste del edge.

**Alcanzable:** trend 0.37, carry 0.495 (no desplegable) — cortos de 0.64. **Qué lo reabriría:** un
bruto DESPLEGABLE medido > 0.64 (CFD) / 0.42 (futuros).

### 2. Amplitud del terreno (`scripts/terrain_breadth.py`, `docs/terrain_breadth.md`)

**N_eff** = número efectivo de apuestas independientes = (Σλ)²/Σλ² sobre los autovalores de la matriz
de correlación de retornos diarios (participation ratio, `terrain_breadth.n_eff`). Techo de IR
≈ IC·√N_eff (Grinold-Kahn).

| universo | N_eff medido | $/mes | techo IR (IC 0.05) | ¿≥0.64? |
|---|---|---|---|---|
| **Cripto perps 30 (Binance, gratis)** | **2.16** | 0 | 0.07 | NO |
| CFD Dukascopy 17 | 5.02 | ~0 | 0.11 | NO |
| ETFs sector/país/factor | 3.31 | 0 | 0.09 | NO |
| Futuros CME ~26 (proxy, el más ancho) | **8.15** | ~50 | 0.14 | NO |

**Por qué 30 perps de cripto valen 2.16 apuestas:** correlación mediana **0.68** — todo co-mueve con
BTC; la cola de altcoins no añade dimensiones. **Por qué N_eff ≥ 14:** para que IC·√N_eff alcance
0.64 con IC 0.05 hace falta √N_eff ≥ 12.8 → N_eff ≥ 164 (techo anual); incluso a rebalanceo mensual
(BR=12·N_eff, el techo realista) hace falta N_eff ≥ **14**, y el máximo accesible es 8.15. **Qué lo
reabriría:** N_eff medido ≥ 14 en un universo accesible.

### 3. Economía del payout (`docs/funded_sharpe_requirement.md`)

`challenge.py` aplicado al ciclo completo: P(éxito) = P(pasar ambas fases) × P(sobrevivir 12 ciclos).
El Sharpe BRUTO mínimo: **~0.5 para P(éxito)≥50% (moneda al aire), ~0.8 para 70-80% (fiable)**.
**Hallazgo: P(quemar)≈0 en el barrido inicial → «el cuello es PASAR, no sobrevivir»** — y su
**corrección posterior** (§4/§6): era un artefacto de barrer sólo vol ≤10% con supervivencia
independiente; con supervivencia acumulativa la barrera SÍ muerde. **Qué lo reabriría:** un bruto
desplegable ≥ 0.5-0.8. Alcanzable: 0.32-0.37.

### 4. Volatilidad objetivo (`docs/funded_vol_sensitivity.md`)

Barrido Sharpe {0.3,0.37,0.5} × vol {8-25%}. En el modelo NORMAL, subir la vol parece MEJORAR el EV
(el payout crece más rápido que la quema: EV/año de $3.4k a $8.3k). **Con los tres caveats reales —
supervivencia acumulativa, colas reales (curtosis 3.2) y límite diario INTRADÍA (×1.8)— se INVIERTE:**
P(quemar 12) a Sharpe 0.37 sube a 0.59 (12%), 0.83 (15%), 0.97 (20%); el EV cae de $3.3k (8%) a
NEGATIVO (20-25%). **Óptimo ~8% → la restricción de vol de §2.1 vindicada.** Qué lo reabriría: nada
del lado de la vol (el óptimo ya es el techo de §2.1).

### 5. Tasa del pipeline (`docs/pipeline_run_001.md`, `_002.md`, `pre_run_003_calibration.md`)

**0 supervivientes de 91** candidatos ciegos. Con 0 éxitos en 91, estimador puntual de la tasa = 0;
cota superior 95% (regla de tres) = 3/91 ≈ **3.3%**. Aun así harían falta **~120 candidatos para UN
superviviente esperado**, ×4 más la restricción de cuatro FAMILIAS distintas → varios cientos; con el
puntual (0), **ningún N finito** da supervivientes. La parada de 200 estaba infradimensionada → el
programa **cierra por TASA, no por agotamiento.** Qué lo reabriría: un track record LIVE ≥3 años, o
un N_eff ≥ 14, o un IC ≥ 0.10 medidos (§4d, `docs/reopening_conditions.md`).

---

## (4) Por qué las curvas que se ven por ahí NO contradicen esto

La pregunta legítima: hay generadores y backtests con curvas espectaculares. ¿Por qué no refutan el
cierre? Con números del propio registro:

**a) StrategyQuant y generadores similares.** Su modelo ES generar/evaluar miles de combinaciones y
quedarse con las mejores in-sample — exactamente el escenario que el Deflated Sharpe corrige. El
factor de degradación reportado→realizado del programa es **0.35** (`costs_model.FACTOR_DEGRADACION:96`,
calibrado con McLean-Pontiff 2016 **0.42** post-publicación, Chen-Zimmermann **~0.5**, y 3 puntos
propios). Aplicado a Sharpes típicos de esas curvas:

| Sharpe de la curva | × 0.35 = realizado esperado | vs listón CFD 0.64 |
|---|---|---|
| 1.0 | 0.35 | NO despeja |
| 1.5 | 0.53 | NO despeja |
| 2.0 | 0.70 | despeja el CFD sólo si el 0.35 es optimista |

Una curva de Sharpe 2.0 in-sample de un generador se realiza ~0.70 esperado — apenas rozaría el CFD,
y por debajo del duty-ajustado (0.96). Y eso ANTES de la amplitud (§3.2).

**b) Curvas de NinjaTrader / backtests manuales sin IC.** Una curva sin intervalo de confianza no
distingue un edge real de suerte. Caso propio: el Sectoral Momentum, **25 años y 9 sectores**, da
SE(Sharpe) ≈ 0.19 → **IC95 [0.17, 0.93]** (`docs/candidate_sectoral_screen.md`). Una curva de Sharpe
0.55 «bonita» es indistinguible de 0.2 o de 0.9. SE(Ŝ) ≈ √((1+S²/2)/T): con 5 años de datos diarios
el SE de un Sharpe anual ≈ 0.45 → un «Sharpe 1.0» tiene IC95 ~[0.1, 1.9]. **Sin intervalo, la curva
no dice nada.**

**c) Sesgo de supervivencia, con la aritmética propia.** A una barrera doble simétrica, a edge CERO,
P(pasar) = a/(a+b) = **0.5** (`challenge.analytic_pass_probability:378`); en el challenge de dos fases
medido, ~0.26 a edge cero (`funded_vol_sensitivity`, S=0). El documento maestro §2.1 lo cifra en
**~33%**. En cualquier caso: **de ~1000 traders SIN ventaja, cientos pasan y publican una curva
ganadora** — no porque tengan edge, sino porque la barrera deja pasar a una fracción grande por azar.
Lo que ves publicado está pre-filtrado por supervivencia.

**d) Qué evidencia SÍ contradiría el cierre — como criterio, no retórica:**
1. Un **track record LIVE** (no backtest) de **≥3 años** con su IC medido.
2. Un **N_eff medido ≥ 14** en un universo accesible (`scripts/terrain_breadth.py`, no proxies).
3. Un **IC medido ≥ 0.10** en algún efecto, out-of-sample, con IC95 que no cruce 0.10.

Si aparece cualquiera de las tres, el cierre se reabre (`docs/reopening_conditions.md`). Ninguna de
las tres se cumple hoy.

---

## (5) Lo que SÍ funcionó

- **Motor validado EXTERNAMENTE:** H001 neto **0.08-0.14** vs SG CTA Trend **0.14** en la misma
  ventana. No medimos de menos ni de más — reproducimos el número de la industria.
- **Simulador verificado contra fórmula cerrada** (`challenge.analytic_pass_probability:368`), no
  contra intuición.
- **Diversificación por familia MEDIDA** (`scripts/family_breadth.py`): trend/carry/estacionalidad
  correlacionan **0.05-0.13 (media 0.09)** → **N_eff de estrategias 2.95 de 3**. A diferencia de los
  instrumentos, las estrategias SÍ se diversifican — combinar familias multiplica el BR como predice
  la teoría. **El cuello nunca fue combinar; fue producir la primera.**
- **Dos hallazgos empíricos PROPIOS en microestructura cripto:** ĉ ≈ 2.5-3.0 (el display del mejor
  nivel sobreestima ~5-6× la profundidad que absorbe flujo, estable a 1s-30s); el trade imbalance NO
  queda subsumido por el OFI en cripto (al revés que en acciones).
- **Validación externa de una CONCLUSIÓN propia:** arxiv:2608.21888 mide, en cripto, el mismo muro
  coste-supera-señal (edge 1.3bp < 5bp) que el programa encontró con OFI/H008.
- **Seis veces una medición refutó una expectativa comprometida o al reviewer:** (1) carry pasó el
  cribado que se esperaba que fallara (neto 0.282); (2) H007 salió UNDERPOWERED en vez de confirmar
  el marco de trend; (3) el sesgo de calibración +0.057 se refutó (ancla mal citada → «no hay
  calibración todavía»); (4) el «H008 supera al nulo → los niveles llevan información» se retractó
  (nulo defectuoso); (5) el «P(quemar)≈0 → el cuello es pasar» se refutó (artefacto doble); (6) el
  temor de que trend y carry correlacionaran 0.6 se refutó (miden 0.09).

---

## (6) Los sesgos que el programa corrigió en sí mismo

- **P(quemar)≈0 era un ARTEFACTO DOBLE:** barrido truncado a vol ≤10% + supervivencia INDEPENDIENTE
  (p^12, optimista). Con supervivencia acumulativa y hasta vol 25%, la barrera muerde
  (`docs/funded_vol_sensitivity.md`). Ejemplo de que el sistema corrige sus propias conclusiones.
- **El sesgo de calibración +0.057** venía de un ancla MAL CITADA: el Sharpe 1.2 de Moskowitz-Ooi-
  Pedersen está en **Figure 2**, no en texto (`docs/extraction_defects.md` D2). La regla anti-
  alucinación (a) lo dejó en null; se marcó `ancla_defectuosa` y se concluyó **«no hay calibración
  todavía»**.
- **El test de coincidencia de H008 estaba MAL EMPAREJADO:** comparaba VAH (interior) vs el extremo
  del día → coincidencia baja garantizada por geometría. Re-emparejado interior-vs-interior (26%,
  `docs/h008_block4.md`).
- **El benchmark nulo de H008 tenía la GEOMETRÍA ROTA:** aleatorizaba la entrada sin reposicionar
  objetivo/stop → Sharpe −3.4 en todos los percentiles; la afirmación «supera al nulo» se RETIRÓ, y
  nació el eje adversario `nulo_preserva_geometria` (`src/pipeline/adversarial.py`).
- **Bug de base en el veredicto de H008:** la condición (3) comparaba el Sharpe de perfil sobre el
  subconjunto compartido (−2.38) contra el nulo de todos los episodios; corregido a la misma base
  (−0.067), lo que cambió el veredicto de «muerta por (3)» a «no viable, (1) underpowered».

---

## (7) El mapa de lo que falta — restricciones con su precio

| restricción | qué habilitaría | precio / bloqueo |
|---|---|---|
| Sin **tasas** (rates) intradía/futuros | familia macro/carry con amplitud | Norgate ~$50/mes → N_eff futuros 8.15 (< 14, no cierra el hueco) |
| Sin **energía** consolidada | más instrumentos descorrelacionados | idem futuros CME |
| Sin **opciones de acciones** / vol implícita | H004 volatility risk premium en equity | Databento $199/$1750 (BANEADO por ToS); Deribit gratis reabre sólo cripto |
| Sin **intradía con volumen consolidado** | volume profile / microestructura en futuros | IQFeed ~$133/mes > presupuesto $125 |
| **Margen CFD 0.42 bp/día** | bajar el suelo de costes | estructural del vehículo CFD (no negociable) |
| **N_eff máximo accesible 8.15** | el techo de amplitud | ningún universo pagable llega a 14 |

**Las tres condiciones de reapertura, con su número actual (`docs/reopening_conditions.md`, ninguna
se cumple):**
- **C1 — Amplitud:** N_eff medido ≥ 14 → hoy **8.15** (futuros, el más ancho accesible).
- **C2 — Señal:** IC ≥ 0.10 medido OOS → hoy **0.077** (mejor implícito, H002 = 0.495/√(3.41·12)).
- **C3 — Objetivo:** revisado a la baja Y algo desplegable despeja → bajado a **0.20** el listón cae
  a ~0.44 y nada desplegable lo supera (carry 0.495 no es desplegable por concentración).

---

**Cierre.** El programa no encontró una estrategia — encontró, con cinco medidas independientes y
convergentes, que el terreno accesible no contiene una que despeje el suelo, y midió exactamente por
qué (amplitud). Lo que sí construyó: un motor validado, un simulador verificado, un pipeline honesto
con un adversario de once ejes, y la disciplina de matar cada idea por la razón correcta y de
corregir sus propios errores. Si alguna de las tres condiciones de reapertura se cumple con su
número, se reabre. Hasta entonces, cerrado — y auditable línea por línea.
