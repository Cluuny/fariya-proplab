# Veredicto del programa — dos ciclos cerrados (CFD y cripto)

Este es el documento de referencia del programa. Cubre AMBOS ciclos —el universo CFD y el
pivote a cripto/order flow— con los números completos y sin adornos. Se consultará dentro
de un año: debe bastar por sí solo.

Dos ciclos, ocho familias con veredicto, **cero supervivientes**. No es un fracaso: es lo
que produce un programa con falsadores honestos, suelo de costes medido y veredictos sin
adornos cuando el vehículo y los datos no dan un edge que supere el suelo.

## Las ocho familias, con veredicto y números (1.1)

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

(H004 volatility risk premium quedó **fuera por datos** — necesita opciones/vol implícita —
sin llegar a veredicto de familia; no cuenta entre las ocho.)

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

**Cumplida: 8 de 8 familias con veredicto, cero supervivientes.** Se declara cumplida y se
registra que **NO se buscó una novena familia.** Cualquier nueva familia sólo puede entrar
si sale del pipeline de investigación y pasa el filtro #6 de costes — no de una intuición.

## Cierre

Dos ciclos, dos vehículos (CFD spot y cripto perp), ocho familias, cero edge que supere el
suelo. El programa convirtió "¿funciona X?" en números falsables y mató cada idea por la
razón correcta antes de arriesgar capital. Lo que sigue no es otra familia: es medir la
degradación backtest-vs-vivo con capital propio (`docs/own_capital_phase.md`), una fase de
INSTRUMENTACIÓN, no de ingreso.
