# Pipeline de investigación — el esqueleto (Flujo 2, estaciones 1-3)

## Por qué existe

Las siete hipótesis del proyecto vinieron de **una sola fuente** (el reviewer). Cinco de
siete fueron **precio puro**. Nunca se leyó un paper completo — se trabajó con resúmenes.
Esa dependencia de fuente única es un **fallo estructural** del programa, tan importante
como el suelo de costes. Este pipeline lo corrige: da al sistema un flujo propio de
candidatos, un filtro barato y un **registro de aprendizaje** que mide (no asume) qué
clase de idea sobrevive.

## Corrección de arquitectura vs. el diseño de junio

El diseño original ponía la **extracción de calidad** primero. Ahora sabemos que el filtro
que más mata es la **ARITMÉTICA DE COSTOS**: H005 y H006 murieron **sin correrse**, por
aritmética. Ese filtro va ANTES de leer el paper — es más barato y más discriminante que
la revisión adversaria.

```
  1. Descubrimiento          discover.py
  2. Triaje de operabilidad  triage_operability.py
  3. TRIAJE DE COSTOS        triage_costs.py     <-- nuevo, antes de leer nada en profundidad
  4-7. (fuera de alcance por ahora — sólo si el mes de futuros da luz verde:
        extracción con LLM, revisión adversaria, generación de stubs)
```

## Estación 1 — Descubrimiento (`src/pipeline/discover.py`)

Fuentes con acceso programático, en orden de facilidad:
- **arXiv API** (q-fin.PM, q-fin.ST, q-fin.TR) — la única con API limpia (Atom).
- **RSS de Alpha Architect** y **RSS de CXO Advisory**.
- **SSRN**: sin API pública → ingesta **manual** de URLs (`manual_candidate`).

Salida: cola de candidatos SIN procesar en la DB (título, abstract, url, fecha, fuente).
El **parseo** (`parse_arxiv_atom`, `parse_rss`) es puro y testeado sobre fixtures; la red
se toca sólo en `fetch_*`, y una fuente caída se salta sin tumbar el resto.

**Cron: MENSUAL, no diario.** El throughput real del sistema es ~una hipótesis al mes;
generar 50 fichas semanales fabrica inventario muerto.

## Estación 2 — Triaje de operabilidad (`src/pipeline/triage_operability.py`)

Con título + abstract, rechaza si: cross-sectional de acciones (universo > 100), requiere
datos que no tenemos (opciones, intradía con volumen, fundamentales point-in-time),
intradía, o sin regla operativa identificable. Salida: keep/reject + razón en una línea.

**Alcance:** implementado como **heurística determinista** sobre palabras clave, con una
interfaz limpia donde un modelo pequeño puede sustituir la heurística más adelante. La
extracción con LLM está **fuera de alcance** de este change. Conservador: ante la duda,
`keep` (que caiga en el triaje de costos, más barato).

## Estación 3 — Triaje de costos (`src/pipeline/triage_costs.py`) — EL FILTRO NUEVO

Aritmética pura, reutiliza `costs_model.sharpe_bruto_requerido_duty`. Cada candidato
declara (estimado del abstract): `duty_cycle_estimado`, `turnover_estimado`,
`bruto_reportado`. El sistema calcula el bruto requerido y rechaza si el reportado no lo
supera. Si el abstract no reporta bruto → `requiere_lectura` (no se descarta; baja
prioridad).

**Parametrizado por VEHÍCULO:** el requerido con CFD (0.64 a duty 100%) y con futuros
(0.424) son distintos porque el suelo de costes es distinto. El pipeline evalúa contra
**ambos**: pasa si supera el requerido en al menos uno.

## Esquema de ficha + registro de aprendizaje (`src/pipeline/db.py`)

Base **estructurada** (SQLite), **NO un RAG**. La búsqueda vectorial produce un chatbot;
lo que hace falta es una **cola ordenable**:

```sql
SELECT * FROM hipotesis WHERE estado='en_cola' ORDER BY score_prioridad DESC LIMIT 1
```

Campos base: los de la ficha probada en H001/H003/H007. **Campos nuevos obligatorios — el
registro de aprendizaje:**

- `clase_de_dato`: precio | macro | flujo | fundamental | estructura_temporal | calendario
- `fuente_de_la_idea`: pipeline | humano | reviewer
- `bruto_esperado` (float, committeado antes de correr)
- `bruto_medido` (float, post-ejecución)
- `duty_cycle_real` (float, post-ejecución)

Permiten preguntar con SQL, no con opiniones: ¿qué clase de dato sobrevive más?, ¿las
expectativas están calibradas o infladas?, ¿las ideas del pipeline sobreviven más que las
humanas?

**SESGO A EVITAR:** NO filtrar a favor de macro/fundamentales porque "parecen las buenas".
La evidencia real es **1 de 2** (carry acertó con 0.28; COT dio cero exacto). Si el
pipeline se construye asumiendo la conclusión, sólo cambia un sesgo por otro. El sistema
**MIDE** la tasa de supervivencia por clase, no la asume.

## Backfill — las 7 hipótesis como conjunto de validación (`src/pipeline/backfill.py`)

H001, H002, H003, H005, H006, H007 y COT, cargadas al esquema nuevo con su clase de dato,
fuente (todas `reviewer`), esperado y medido. Es el **conjunto de validación**: si el
sistema no reproduce los veredictos conocidos, está mal construido. Reproduce:
**cero supervivientes** y **5/7 de clase precio**.

Primer reporte de aprendizaje (`learning_report.py`, `pipeline report`):

| clase_de_dato | n | vivas | tasa |
|---|---|---|---|
| precio | 5 | 0 | 0% |
| calendario | 1 | 0 | 0% |
| flujo | 1 | 0 | 0% |

Calibración (sólo las 3 corridas con esperado+medido): sesgo medio **+0.057** →
en promedio **sobreestimamos** el bruto, dominado por H001 (Grinold-Kahn predijo un edge
de trend que no estaba). H007 quedó on-target pero underpowered. La conclusión honesta NO
es "todo inflado" sino "las expectativas de trend por amplitud estaban infladas".

## Uso

```bash
python -m scripts.pipeline init         # crea el esquema
python -m scripts.pipeline backfill     # carga las 7 hipótesis conocidas (validación)
python -m scripts.pipeline discover     # estación 1 (cron MENSUAL)
python -m scripts.pipeline triage       # estaciones 2 y 3 sobre candidatos
python -m scripts.pipeline report       # reporte de aprendizaje
python -m scripts.pipeline queue        # la siguiente hipótesis en cola
```

## Alcance de este change (research-pipeline-v1)

Sólo estaciones 1-3 + esquema + registro de aprendizaje + backfill. **NO** extracción con
LLM, **NO** revisión adversaria, **NO** generación de stubs — eso se construye sólo si el
mes de futuros da luz verde. Presupuesto: ~8-10 horas, no 4 semanas.

---

# Extensión: intradía y microestructura (change research-pipeline-intraday)

El pipeline asumía EOD implícitamente. Las hipótesis de microestructura (order flow,
volume profile, AMT) quedaban fuera **por omisión, no por evaluación**. Ahora **compiten en
igualdad**, con su listón de costos correcto.

## Campos nuevos del esquema

- `frecuencia`: **EOD | intraday_bar | tick | orderbook**
- `requiere_volumen_consolidado` (bool — FX spot NO lo tiene; futuros SÍ)
- `requiere_cinta_tick` (bool), `requiere_order_book_l2` (bool)
- `costo_datos_usd_mes` (coste de datos de **primera clase**)
- `trades_por_dia_estimado`, `contrato_ref` (para el suelo intradía)
- `requiere_test_incremental` (volume profile vs niveles simples)

## Estación 3 extendida a intradía

En intradía el coste lo domina **rotar**, no mantener. La estación 3 enruta por
`frecuencia`: EOD → suelo swing por duty (CFD 0.64 / futuros 0.424); intradía → suelo por
rotación (`sharpe_bruto_requerido_intraday`, ver `docs/cost_floor.md`). **Advertencia
calibrada:** por encima de ~1.4 round-trips/día en ES (0.4 en CL) el coste intradía supera
el 1.96%/año del margen CFD que mató seis hipótesis.

## Costo de datos como campo de primera clase — niveles y precios VERIFICADOS

La estación 2 rechaza si `costo_datos_usd_mes` excede el presupuesto (por defecto **60
USD/mes**). Qué habilita cada nivel (precios consultados 2026-08-24):

| nivel | proveedor / precio | habilita | NO habilita |
|---|---|---|---|
| **EOD futuros continuos** | Norgate **~$22.50/mes** ($270/año, EOD) | swing, carry de estructura temporal, volumen a nivel DIARIO | tick, volumen intradía |
| **Barras 1-min + volumen** | IQFeed **~$133/mes** (core $108.15 + futuros $24.87, dtn 2025-12) | volume profile, AMT estructural, order flow aproximado (Lee-Ready sobre tick+L1) | order book L2/L3 real |
| **Tick / cinta completa** | Databento usage-based ($125 crédito inicial) o Standard **$199/mes** (1 mes de historia) | order flow, delta, footprint | profundidad L2/L3 con historia larga |
| **Order book L2/L3** | Databento **Plus $1 750/mes** (16+ años, MBP-10/MBO) | imbalance, VPIN | — (el más caro) |

**Con presupuesto $60/mes sólo entra EOD (Norgate).** Volume profile / order flow quedan
`rechazada_por_datos` hasta subir el presupuesto — con el proveedor y precio anotados en la
ficha, para que la decisión sea explícita y no una omisión.

## Regla de falsabilidad para la familia (filtro #1, distinción de CATEGORÍA)

La estación 2 rechaza por no-falsabilidad. **ADMITIDAS** (miden un dato externo y
verificable, existe en un archivo de datos): order flow (agresores vs pasivos, requiere
cinta), volume profile (volumen por nivel, requiere volumen real), VPIN/imbalance (Easley,
López de Prado, O'Hara), microestructura clásica (Kyle 1985, Glosten-Milgrom).
**RECHAZADAS por NO falsables**: ICT / SMC (order blocks, fair value gaps, "liquidez
institucional") — se definen sobre el gráfico mismo; un "order block" se identifica
dibujándolo después, no consultando dónde había órdenes. No hay dato externo que lo
confirme ni lo refute. Es una distinción de **categoría, no de estilo ni prejuicio**.

## Regla de test incremental para volume profile

Requisito de diseño para cualquier hipótesis de volume profile (marcada con
`requiere_test_incremental`): el test NO es "¿funciona el volume profile?" sino **"¿el
VAH/VAL/POC aporta información INCREMENTAL sobre niveles de precio simples (máx/mín de N
días, medias móviles, bandas de volatilidad)?"**. Se corre con niveles simples, luego con
niveles de perfil, y se mide la DIFERENCIA. Si el VAH y el máximo de 20 días marcan el
mismo precio el 80% del tiempo, la maquinaria de perfiles es infraestructura cara para
reproducir algo gratis.

## Fuentes de descubrimiento ampliadas

La estación 1 añade un barrido de TÉRMINOS de microestructura sobre arXiv q-fin.TR
(infrarrepresentado por categoría): order flow imbalance, market microstructure, limit
order book, price impact, VPIN, trade classification, high frequency.

## Backfill de microestructura

Además de las 7 EOD (todas `costo_datos` 0), el backfill carga dos casos de microestructura
como conjunto de validación de los filtros nuevos:
- **AMT / Volume Profile** (`MP001`) → `rechazada_por_datos` (necesita IQFeed ~$133/mes >
  $60; Norgate EOD no lo habilita; + requiere test incremental).
- **ICT / SMC** (`ICT001`) → `rechazada_por_falsabilidad` (order blocks/FVG no miden un dato
  externo). Nota: su `costo_datos` es 0 (se dibuja sobre el gráfico) y AUN ASÍ se rechaza —
  la falsabilidad se comprueba ANTES que el presupuesto.

El reporte de aprendizaje añade la **distribución por frecuencia** (EOD 7, intraday_bar 2).

---

# Pipeline COMPLETO — estaciones 4-7, fuentes no académicas, presupuesto $125 (change research-pipeline-full)

Motivo estructural: 7 de las 8 familias con veredicto salieron del reviewer; 5 de 8 fueron
precio puro; nunca se leyó un paper completo. **El pipeline existe para romper esa
dependencia y se juzga por si produce supervivientes que el reviewer NO habría propuesto.**

Parámetros del operador: **presupuesto de datos $125/mes**, **condición de parada 200
candidatos** (`docs/pipeline_stop_condition.md`), alcance estaciones 1-7.

## Presupuesto de datos — $125/mes (precios verificados 2026-08-24)

| ADMITE | precio | habilita |
|---|---|---|
| Norgate futures EOD | ~$50/mes ($270/año) | swing en futuros, continuos roll-adjusted |
| Binance data.binance.vision | gratis (ya ingerido) | order book / trades cripto |
| **Deribit API pública** | **gratis** | **opciones cripto BTC/ETH, DVOL — volatility risk premium (la clase que faltaba desde H004)** |
| BIS / FRED / CFTC COT | gratis (ya ingeridos) | macro, posicionamiento |
| LOBSTER samples | gratis | order book de muestra |

| NO ADMITE (rechazo en estación 2, precio anotado) | precio |
|---|---|
| Opciones de acciones / SPX (gamma, 0DTE sobre índices) | ≫ $125 |
| Databento Standard / Plus | $199 / $1.750 |
| Polygon | $199 |
| IQFeed | ~$133 (**frontera**, marginalmente por encima) |
| dxFeed, CQG | enterprise |

**REGISTRADO: Databento BANEADO** (violación de ToS por múltiples cuentas). NO se crean
cuentas nuevas en ningún proveedor para evadir límites.

## Estación 1 ampliada — fuentes NO académicas

Además de arXiv/RSS: **Reddit, Twitter/X, Discord, YouTube** por ingesta manual de URLs
(`discover.manual_candidate(..., tipo_de_fuente=...)`). **Condición innegociable:** pasan por
los MISMOS filtros. Una afirmación sin regla operativa, sin universo, sin mecanismo y sin
falsador NO es hipótesis, es contenido — y la estación 2 la rechaza. La **tasa de rechazo por
tipo de fuente** es un resultado del pipeline (learning_report): dice si las no académicas
producen algo testeable.

## Estación 3 recalibrada — listones medidos de ambos ciclos

`triage_costs.LISTONES_REFERENCIA`: CFD swing 8% → **0.64**; cripto perp mejor caso → **0.65**
(maker+1rt/día+funding evitado); capital propio 20% vol → **0.50** (SÓLO si la vol extra viene
de instrumentos más volátiles al mismo notional, NO de apalancamiento — coste/vol invariante,
verificado); duty bajo → Sharpe ACTIVO requerido `0.40/√duty+0.245` (SUBE, no baja).

## Estaciones 4-7 (nuevas)

- **4. Extracción** (`extract.py`): PDF completo → ficha, structured output. Dos reglas
  anti-alucinación IMPUESTAS por validación: (a) cada campo numérico exige **cita de
  ubicación** (sección/tabla) o va a null; (b) **sin falsador escribible, se rechaza por
  esquema** (no se acumulan "ideas interesantes"). La llamada LLM es el `seam`.
- **5. Revisión adversaria** (`adversarial.py`): segundo agente, prompt DISTINTO, único
  trabajo destruir la ficha. Ocho ejes de ataque; los críticos incluyen las lecciones de H003
  (¿benchmark cero o comparte exposición?) y del OFI (¿contemporáneo o PREDICTIVO?). Un eje
  crítico fallado → reject. Los LLM son aduladores hacia el texto que leen; el adversario lo
  contrarresta.
- **6. Generación de stub** (`stub_gen.py`): ficha aprobada → función en `signals.py` con el
  contrato fijo (precios→pesos) y `NotImplementedError`. El motor no cambia; la señal se
  implementa a mano contra el contrato, no la inventa el LLM.
- **7. Compuerta humana** (`human_gate.py`): 15 min/mes, 3-5 candidatos, se aprueba UNO
  (→ pre_registrado). El pipeline no auto-aprueba nada.

## Registro de aprendizaje — campos nuevos

`tipo_de_fuente` (paper_arbitrado/preprint/blog/reddit/twitter/discord/youtube),
`causa_de_muerte` (coste/amplitud/efecto_inexistente/datos/falsabilidad/concentracion),
`clase_de_dato` +`volatilidad_implicita`. Consultas con SQL (learning_report): supervivencia
por clase y por tipo de fuente, calibración de expectativas, y **la clave — ¿sobreviven más
las ideas del pipeline que las del reviewer?** (el test de si el pipeline valió la pena).

## Backfill = conjunto de validación (11)

Las 8 con veredicto (H001/H002/H003/H005/H006/H007/COT/OFI, todas fuente=reviewer) + H004
(rechazada_por_datos; **Deribit la reabre**) + AMT/volume profile (rechazada_por_datos) +
ICT/SMC (rechazada_por_falsabilidad). Reproduce los veredictos conocidos: cero supervivientes,
**5/8 precio** entre las familias, **8/8 reviewer**, causa de muerte dominada por coste (5).
Si el pipeline no los reprodujera, estaría mal construido.
