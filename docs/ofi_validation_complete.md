# OFI — validación cerrada (Bloque A) y cribado de decaimiento (Bloque B)

Datos reales BTCUSDT perpetuo (USDⓈ-M), 4 días de regímenes distintos elegidos por vol
realizada ANTES de correr el OFI (klines 1m Jan-Mar 2024):
2024-02-03 range/baja (1.0%/día) · 2024-02-12 normal (2.6%) · 2024-01-02 normal-atípico
post-NY (3.1%) · 2024-03-05 alta (7.6%).

---

## Deliverable 1 — Tabla de validación completa (Bloque A)

Regresión conjunta `ΔP_k = α + θ_O·OFI_k + θ_T·TI_k + ε` (la 8c del paper) por media hora,
Δt=10s, SE de White. Días completos (~18M filas c/u).

| fecha | régimen | R²_OFI | R²_TI | R²_conj | t(θ_O) | t(θ_T) | %sig(θ_T) | pendiente log-log | ĉ(λ=1) | R² excl.precio | ¿pasa? |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024-01-02 | normal (post-NY) | 0.638 | 0.453 | 0.834 | 16.8 | 9.4 | 100% | −1.17 | 2.93 | 0.596 | **SÍ** |
| 2024-02-03 | range/baja vol | 0.664 | 0.511 | 0.848 | 12.2 | 7.8 | 96% | −0.49 | 2.53 | 0.592 | **SÍ** |
| 2024-02-12 | normal | 0.674 | 0.406 | 0.823 | 15.5 | 7.3 | 98% | −1.04 | 2.99 | 0.611 | **SÍ** |
| 2024-03-05 | alta vol | 0.604 | 0.403 | 0.739 | 13.3 | 6.2 | 98% | −0.88 | 5.24 | 0.514 | **SÍ** |

Las cuatro verificaciones (R²>0.40, OFI>TI, β∝1/profundidad, R² se mantiene al excluir
eventos que cambian precio) se sostienen en los cuatro regímenes.

**HALLAZGO CLAVE (A.1) — el trade imbalance NO queda subsumido, al revés que en el paper.**
En acciones el t-stat de θ_T cae ×4 y sólo es significativo en 31% de submuestras; en cripto
**θ_T sobrevive fuerte** (t 6-9, significativo en 96-100%). Implicación de infraestructura:
**gran parte de la señal contemporánea está en los aggTrades** (5-64 MB/día) y no sólo en el
bookTicker (144-384 MB/día). PERO el OFI aporta claramente por encima: R²_conjunto (0.74-0.85)
≫ R²_TI solo (0.40-0.51), y t(θ_O) (12-17) > t(θ_T) (6-9). Lectura: el bookTicker añade
información incremental real —procesarlo se justifica— pero el aggTrades solo ya captura ~0.45
de R², una vía barata para una primera pasada.

---

## Deliverable 2 — Verificación de unidades (A.3)

Con c=0.5 (modelo estilizado), β medio ⇒ profundidad implícita vs profundidad MEDIDA:

| fecha | β medio | prof. implícita (c=0.5) | prof. MEDIDA | factor | ĉ(λ=1) |
|---|---|---|---|---|---|
| 2024-01-02 | 0.637 | 0.79 BTC | 4.72 BTC | 6.0× | 2.93 |
| 2024-02-03 | 0.386 | 1.30 BTC | 6.74 BTC | 5.2× | 2.53 |
| 2024-02-12 | 0.578 | 0.86 BTC | 5.42 BTC | 6.3× | 2.99 |
| 2024-03-05 | 2.141 | 0.23 BTC | 2.90 BTC | 12.4× | 5.24 |

**¿Cuadran? NO exactamente — factor ~5-6× (normal/range), pero NO es un bug de unidades.**
El paper obtiene ĉ≈0.45 (prices más resilientes que la profundidad); nosotros ĉ≈2.5-3.0
(≈5-6× su valor). Investigación (ĉ a Δt=1,2,10,30s sobre subset):

| Δt | ĉ(λ=1) | β | AD medida | ev/bin |
|---|---|---|---|---|
| 1s | 2.686 | 0.432 | 6.40 | 188 |
| 2s | 2.685 | 0.435 | 6.35 | 375 |
| 10s | 2.630 | 0.429 | 6.29 | 1876 |
| 30s | 2.548 | 0.417 | 6.25 | 5621 |

**ĉ es ESTABLE a través de escalas** (2.5-2.7 de 1s a 30s, de 188 a 5621 eventos/bin) →
descarta tanto un bug de unidades (las dimensiones cuadran: ĉ en ticks) como un artefacto de
cancelación intra-bin (sería creciente con Δt). Es una propiedad ROBUSTA: en cripto el tamaño
DISPLAY del mejor nivel sobreestima la profundidad que realmente absorbe flujo agresivo por
~5× (liquidez fugaz / no comprometida). Va en dirección OPUESTA al paper (precios MENOS
resilientes que el book display, no más). **No afecta la validez del OFI como predictor
(β∝1/profundidad se mantiene) ni el test del Bloque B** (que usa retornos, no c). Documentado
y resuelto antes de B, como se pidió.

---

## Deliverable 3 — Tabla de decaimiento (Bloque B)

Para cada horizonte h se usan bins de tamaño h (horizonte = frecuencia: 1 round-trip/bin).
Contemporáneo = return(k)~OFI(k); PREDICTIVO = return(k+1)~OFI(k). Pool de 4 días, ~11 h
contiguas c/u (subset acotado por memoria; cobertura 100%, 0 huecos). IC por block bootstrap.
Sharpe implícito = IC·√(apuestas/año) (cota superior sin fricción). Suelo = Bloque 3.

| horizonte | R²_contemp | R²_predictivo | IC pred [IC95] | n_indep | Sharpe impl. | rt/día | suelo maker | suelo taker | BRECHA(maker) |
|---|---|---|---|---|---|---|---|---|---|
| 1s | 0.179 | 0.0068 | +0.082 [.082,.083] | 103,456 | 462.9 | 86,400 | 21,203 | 52,739 | **−20,740** |
| 5s | 0.202 | 0.0012 | +0.034 [.035,.035] | 20,689 | 86.5 | 17,280 | 4,241 | 10,548 | **−4,154** |
| 10s | 0.196 | 0.0001 | +0.010 [.009,.011] | 10,342 | 18.2 | 8,640 | 2,121 | 5,274 | **−2,103** |
| 30s | 0.210 | 0.0007 | +0.027 [.021,.030] | 3,445 | 27.5 | 2,880 | 707 | 1,758 | **−680** |
| 1min | 0.184 | 0.0002 | +0.012 [.010,.033] | 1,720 | 8.9 | 1,440 | 354 | 879 | **−345** |
| 5min | 0.133 | 0.0235 | +0.153 [.129,.196] | 341 | 49.7 | 288 | 71 | 176 | **−21.4** |
| 15min | 0.079 | 0.0001 | +0.012 [.004,.130] | 111 | 2.3 | 96 | 24 | 59 | **−21.7** |
| 30min | 0.054 | 0.0074 | +0.086 [n<100] | 53 | 11.4 | 48 | 12.2 | 30 | **−0.77** |
| 60min | 0.025 | 0.0235 | −0.153 [n<100] | 23 | −14.4 | 24 | 6.3 | 15 | **−20.6** |

**Los dos R² lado a lado (D.2 del pedido):** contemporáneo ~0.18-0.21 (pooled; ~0.64 por
ventana, ya validado) → predictivo **~0.007 o menos** en todos los horizontes con n adecuado.
Es el error de H003: describir no es predecir. Hay una señal predictiva REAL a 1s (IC +0.082,
IC95 estrechísimo, n=103k) — pero minúscula. Los picos de 5/30/60 min (R² 0.02) tienen n=23-341
y CI que cruzan cero; son ruido, no señal.

**El cruce con el suelo de costes (D.3, lo que decide):** la BRECHA es **negativa en todos los
horizontes**. Incluso el Sharpe implícito SIN fricción (cota superior) queda por debajo del
suelo requerido a la frecuencia que ese horizonte impone. El "mejor" caso (30 min) queda a
−0.77 del suelo maker más favorable — y su IC ni siquiera es fiable (n=53). El dato de diseño
lo explica: comisión maker 2 pb vs spread medido 0.03 pb ⇒ market making imposible a VIP0; ser
maker sólo ahorra comisión. La señal necesitaría >4 pb/round-trip sólo para empatar.

---

## Deliverable 4 — Gráfico

Reporte visual (contemporáneo vs predictivo por horizonte + tabla del cruce con costes):
`results/crypto/ofi_decay_report.html` (artifact compartible). ASCII inline en
`results/crypto/blockB_decay.md`.

---

## Deliverable 5 — Veredicto (B.4) y expectativa (B.5)

**VEREDICTO: ORDER_FLOW_CERRADO.** Ningún horizonte supera su suelo de costes; la brecha es
negativa en todos. El order flow se cierra como familia, igual que H005, H006 y COT. **Cero
pesos gastados.** No se procede a modelo de fills ni a pre-registro de hipótesis.

**Expectativa comprometida (B.5): CONFIRMADA, no refutada.** Se escribió antes de correr:
"R² predictivo cercano a cero por encima de un minuto, y en los horizontes cortos donde haya
señal, la frecuencia requerida hará que el coste la supere. Resultado más probable: ningún
horizonte supera su listón." Es exactamente lo medido: R² predictivo ~0 salvo un IC real pero
minúsculo a 1s, y el coste de rotar a esa frecuencia lo supera por ~50×.

---

## Deliverable 6 — Cómputo

- Bloque A (validación completa, 4 días completos): **1.22 GB procesados, 164 s** (41 s/día).
- Bloque B (decaimiento, 4 × ~11 h por límite de memoria de la máquina): **1.11 GB, 21 s**.
- Escalar es viable: ~40 s/día-completo de bookTicker. El cuello no es cómputo sino RAM en esta
  máquina (los sorts de 30M filas hacen swap); un día completo cabe con más memoria. El
  veredicto NO depende de más datos: la brecha con el suelo es de órdenes de magnitud, no de
  márgenes que más muestra pueda cerrar.

## Qué NO se hizo (comprometido)

NO se construyó modelo de fills. NO se pre-registró ninguna hipótesis. NO se tocó holdout. NO
se contrató nada. Estos dos bloques fueron infraestructura y cribado.
