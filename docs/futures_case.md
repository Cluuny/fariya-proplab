# ¿Migrar a futuros? — el caso, con aritmética y datos gratis

La opción A (migrar a futuros) es atractiva pero cuesta dinero que no hay. Antes de
gastar: ¿el cambio de vehículo baja el suelo de costes lo suficiente para que un bruto
realista sobreviva? La pregunta NO es "¿funciona trend en futuros?" (la industria dio
~0.14 en nuestra ventana). Es sobre el SUELO y la AMPLITUD.

## Criterio de decisión — COMPROMETIDO antes del análisis

La suscripción se justifica SÓLO si se cumplen **LAS DOS**:
1. **Suelo recalculado deja el bruto requerido < 0.50.**
2. **N_eff estimada del universo de futuros > 7.5.**

Si no se cumplen, la opción A queda **CERRADA POR EVIDENCIA**, no por falta de dinero.

---

## Bloque 1 — Coste de mantener en futuros

**Hecho estructural (la clave):** los futuros NO cobran el margen diario de
financiación que domina el suelo del CFD (0.42 bp/día ≈ **1.96%/año**). El carry va
embebido en el precio del futuro (no se cuenta dos veces: la señal lo captura vía
precio). El coste de mantener futuros es: **roll** (spread del calendar spread × ~4
rolls/año) + **comisión** + **spread bid/ask** del front. Sin margen diario.

**Fuentes públicas** (consultadas 2026-08-23):
- Especificaciones de contrato CME (notional, tick value): cmegroup.com.
- Comisión IBKR: **$0.85/contrato/lado**, ~**$4.20 round-trip** all-in
  (interactivebrokers.com/en/pricing, vía búsqueda 2026-01).
- Modelo: roll = 4 × (1 tick de calendar spread); spread front = turnover(~9×) × 1
  tick/lado; comisión = round-trips × $4.20. Turnover como el trend actual.

### Coste de mantener por mercado (%/año)

| clase | mercados baratos (%/año) | mercados caros por ROLL (marcar: NO valen) |
|---|---|---|
| Índices | ES 0.06, NQ 0.02, YM 0.04, RTY 0.07 | — |
| Rates | ZT 0.05, ZF 0.10, ZN 0.19 | ZB 30Y 0.34 (largo, tick grande) |
| FX | 6E 0.07, 6J 0.08, 6B 0.12 | 6A/6C 0.21 |
| Energía | RB 0.10, HO 0.10, CL 0.21 | **NG gas 0.50** |
| Metales | GC 0.03, HG 0.16, SI 0.23 | — |
| Agrícolas | ZS soja 0.28, KC 0.24 | **ZC maíz 0.91, ZW trigo 0.67, SB azúcar 0.82** |

El coste de roll varía MUCHO: índices/rates/FX/oro son baratísimos (0.02-0.19%);
agrícolas y gas natural son caros (0.5-0.9%) — **no valdrían la pena por coste de roll**
y se excluyen del libro operable.

### Suelo recalculado (libro líquido diversificado, `costs_model`)

| | CFD (medido) | Futuros (estimado, libro líquido) |
|---|---|---|
| coste de mantener | **1.96%/año** (margen diario) | **0.19%/año** (roll+spread+comisión, sin margen) |
| coste total | 2.09%/año | 0.19%/año |
| suelo bruto (break-even) | 0.26 | **0.024** |
| **bruto requerido (net > 0.40)** | **0.66** | **0.424** |

**El vehículo baja el bruto requerido de 0.66 a ~0.42 (11× menos coste de mantener).**
→ **Criterio (1) SE CUMPLE** (0.424 < 0.50).

### Contraste contra la mejor evidencia PROPIA

H007 muestra A dio **bruto 0.370** (FX+metales, con 2008). Contra el nuevo listón
(0.424): corto por −0.054. En CFD era 0.370 vs 0.66 = −0.29; en futuros 0.370 vs 0.424
= **−0.054**. De "estructuralmente imposible" a "al borde".

### CORRECCIÓN de comparabilidad del Sharpe (change excess-sharpe-fix)

Antes de comparar contra la industria, dos correcciones:
- **Sharpe de exceso (Problema A):** verificado — nuestros retornos son
  `Σ w·pct_change(precio) − costos` = ganancia de capital pura, SIN interés sobre
  colateral. En una cuenta fondeada no se cobra ni se cobra rf, así que **nuestros
  Sharpes YA son de exceso** y comparables al Sharpe de exceso de la industria. Restar
  rf sería doble-conteo (bajaría H007-A neto 0.184 → 0.023 artificialmente). No se
  corrige ningún número nuestro; el principio (usar exceso) es el correcto y ya lo
  cumplimos. `engine.sharpe(rf=...)` existe para series que SÍ incluyan rf.
- **Comisiones (Problema B):** el **0.14 de la industria (SG CTA Trend) es NETO de
  comisiones de gestión** (ret 2.9% / vol 11% / Sharpe 0.14 → rf implícito ≈1.4%).
  Sumando una comisión de gestión estándar (**~2%**, convención "2 y 20" de CTAs; rango
  1.5-2.5% → Sharpe 0.28-0.37), el **bruto de comisiones ≈ 0.32**. Nuestros backtests
  no pagan comisión de gestión → la comparación correcta es **0.32 (industria, bruto de
  comisiones) vs 0.424 (nuestro requerido en futuros)**.

**El hueco pasa de 3× (0.14 vs 0.42) a ~30% (0.32 vs 0.42).** Y nuestra propia H007-A
(0.370) es de hecho *ligeramente superior* al bruto de la industria (0.32) y a 0.05 del
requerido. El bruto realista de trend (~0.32-0.37) y el requerido de futuros (0.42)
están **a distancia de ruido** — refuerza que el resultado más probable es INDETERMINADO,
no un NO estructural.

**Parcial Bloque 1: criterio (1) cumplido. Falta el criterio (2) — amplitud (Bloque 2).**

---

## Bloque 2 — Amplitud estimada con proxies gratuitos

Universo PROXY del panel de futuros con ETFs de historia larga y EOD gratis (Yahoo
Finance chart API, consultado 2026-08-23; Stooq quedó tras un muro JS). Clases que no
tenemos vía Dukascopy: **rates** (SHY 1-3a, IEF 7-10a, TLT 20a+), **energía** (USO
petróleo, UNG gas), **commodities amplias/agri** (DBC, DBA). Índices y metales ya los
tenemos.

**LIMITACIÓN (explícita):** los ETFs NO sirven para operar (tracking error, expense
ratio, contango propio) — SÓLO para estimar la matriz de correlación. Y su ruido
idiosincrático probablemente **INFLA** el N_eff (más varianza independiente), así que
la cifra es un **techo optimista**.

### N_eff estimada (autovalores, ventana común 2017-2026, 1886 días)

| universo | N_eff | Δ |
|---|---|---|
| 17 CFD (actual) | 5.31 | — |
| + rates (SHY/IEF/TLT) | 6.14 | +0.84 |
| + rates + energía (USO/UNG) | 7.10 | +0.95 |
| **+ rates + energía + commod/agri** | **7.68** | +0.58 |

### Aporte marginal por CLASE (17 + esa clase sola)

| clase | Δ N_eff | ¿construible desde FX+equity? |
|---|---|---|
| rates | **+0.84** | NO → información nueva (como EURCHF +0.51) |
| energía | **+0.98** | NO → información nueva |
| commod/agri | **+0.76** | NO (ag independiente; DBC solapa algo con energía/metales) |

Se confirma la tesis de `breadth-lessons.md`: **bonos y energía NO son recombinaciones
de FX/equity → aportan como EURCHF/HK50 (+0.5/+0.4), no como AUDJPY (+0.05).** Ésa es la
diferencia real entre expandir dentro del mismo span (cruces FX, inútil) y añadir clases
nuevas.

**N_eff estimada = 7.68 → criterio (2) SE CUMPLE (>7.5), pero MARGINALMENTE** y sobre un
techo optimista (ETFs inflan). Techo de Sharpe: √(7.68/5.32) = **×1.20**.

---

## Bloque 3 — Precio real y veredicto

Datos EOD de futuros con **continuos ajustados por roll**. NO Databento (diseñado para
alta frecuencia — sería pagar resolución de microsegundos para hacer swing diario).
Panorama de precios (consultado 2026-08-23; los exactos requieren verificación en el
sitio antes de suscribir — varias páginas usan calculadora interactiva):

| Vendor | Producto | Precio aprox. (USD/mes) | COP/mes (~3037/USD) | nota |
|---|---|---|---|---|
| **Norgate Data** | Futures (~100 mercados, continuos roll-adjusted, **EOD**) | ~22.5 (270/año) | ~68k | el ajuste EXACTO al caso; precio verificado 2026-08-24; **sin tick/volumen intradía** |
| Barchart | planes EOD histórico | ~30-100 | ~90k-300k | tiers |
| Nasdaq Data Link | algunas tablas de futuros | variable | — | cobertura desigual |
| CME DataMine | settlements del exchange | caro/enterprise | — | overkill |

**El más ajustado y barato: Norgate.** Precio VERIFICADO (norgatedata.com, consulta
2026-08-24): **USD 270/año ≈ $22.50/mes equivalente** (sólo términos de 6 o 12 meses, no
hay mensual) — aún más barato que la estimación previa de ~$50/mes. Comparado con una cuota
de challenge (~$500 ≈ **1.5M COP**), el dato cuesta **~1/20 de UN challenge**. La
asequibilidad NO es el cuello de botella.

> **CORRECCIÓN IMPORTANTE (change research-pipeline-intraday): Norgate es EOD.** El mes
> planeado da continuos ajustados por roll de fin de día — **NO habilita order flow ni
> volume profile intradía** (no trae cinta tick ni volumen consolidado intradía). Si el
> destino es microestructura (order flow, footprint, VPIN), requiere **otro proveedor y
> otro presupuesto**: barras 1-min + volumen ≈ **IQFeed ~$133/mes** (core $108.15 + futuros
> $24.87, dtn 2025-12), y order book L2/L3 ≈ **Databento Plus ~$1 750/mes** (databento.com,
> 2026-08-24). Ambos MUY por encima del presupuesto de datos del pipeline ($60/mes). El mes
> de Norgate responde la pregunta de EDGE de trend/amplitud en swing, NO la de
> microestructura. Que no haya confusión: son dos preguntas y dos presupuestos distintos.

### VEREDICTO contra el criterio comprometido

| criterio | umbral | medido | ¿cumple? |
|---|---|---|---|
| (1) bruto requerido | < 0.50 | **0.424** | **SÍ** |
| (2) N_eff estimada | > 7.5 | **7.68** | **SÍ** (marginal) |

**Ambos criterios se cumplen → GO.** El cambio de vehículo SÍ baja el suelo lo
suficiente (0.66→0.42) y SÍ añade amplitud real de clases nuevas (rates/energía, no
recombinaciones) por encima de 7.5.

**Pero es un GO FRÁGIL, dicho sin adornos:**
- El criterio (2) pasa por **0.18** y descansa en un **techo optimista**: los ETFs
  inflan N_eff por su ruido idiosincrático. Con continuos de futuros reales el N_eff
  podría caer por debajo de 7.5 → el (2) podría voltearse a NO-GO.
- El coste baja el listón a 0.42, pero **ninguna familia accesible ha producido 0.42 de
  bruto**: la mejor evidencia propia es H007-A 0.370 (corto por 0.05). La industria da
  0.14 NETO de comisiones, ≈**0.32 bruto de comisiones** (ver corrección arriba) — de
  hecho por debajo de nuestra H007-A. **El GO compra un vehículo mejor, NO una
  estrategia.** El problema del edge sigue sin resolver (el hueco realista es ~30%, no 3×,
  pero sigue del lado corto).

**El veredicto GO/NO-GO NO cambia con la corrección de exceso/comisiones.** El criterio
comprometido depende de dos números (bruto requerido < 0.50 y N_eff > 7.5); ninguno se
mueve. La corrección sólo reencuadra la *magnitud* del hueco de edge (de 3× a ~30%),
haciéndolo aún más claramente una zona de ruido/indeterminación que un NO estructural —
lo que refuerza, no cambia, el GO frágil.

**Decisión de bajo arrepentimiento:** como el dato cuesta ~1/10 de un challenge ya
presupuestado, el movimiento coherente con el GO marginal es **adquirir UN mes de
Norgate, reconstruir el N_eff con continuos REALES y re-verificar el criterio (2)** antes
de comprometer más — el coste de comprobar es despreciable, y decide el (2) con datos en
vez de proxies. Si el N_eff real cae < 7.5, la opción A queda CERRADA POR EVIDENCIA.
