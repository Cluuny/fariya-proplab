# Triaje de la cola por filtro #6 (coste) — semana 9

El suelo lo domina el margen, proporcional al **duty cycle** (fracción de días con
posición abierta). Criterio de admisión, POR ENCIMA del orden de la cola:

    sharpe_bruto_requerido ≈ 0.24 × duty_cycle + 0.40   (costs_model.sharpe_bruto_requerido_duty)
    duty 100% → 0.64   ·   50% → 0.52   ·   20% → 0.45   ·   10% → 0.42

**Trampa — el duty bajo NO baja el listón (corrige un error de framing):** el bruto de
una estrategia de duty bajo se mide sobre TODA la serie, flat days incluidos. Un
efecto grande en 20 días/año se diluye al anualizar (`Sharpe_whole ≈ Sharpe_activo ×
√duty`). El número de decisión es el **Sharpe del período ACTIVO requerido**, que
**SUBE** al bajar el duty:

    Sharpe_activo requerido = 0.40/√duty + 0.245   (costs_model.sharpe_activo_requerido)
    duty 100% → 0.645 · 50% → 0.81 · 20% → 1.14 · 10% → 1.51

El requerido de serie completa (0.24·duty+0.40) baja con el duty, pero el alcanzable
se diluye igual → duty bajo exige un edge ACTIVO mucho más fuerte, no más débil.

## Tabla de triaje (entradas vivas)

| Hipótesis | duty | turnover | bruto requerido | bruto plausible | veredicto |
|---|---|---|---|---|---|
| **H002** carry | 100% | ~9× | **0.64** | **0.495** (medido, gross spot+carry) | **RECHAZADA-POR-COSTE** |
| **H005** reversión corto plazo | ~100% | 50-100× | **0.78** (0.64 + spread de rotación) | 0.3-0.5 (literatura índices) | **RECHAZADA-POR-COSTE** |
| **H006** intermarket/macro | ~100% (price-based, siempre-en) | medio | ~0.64 | sin evidencia de bruto alto; lead-lag decaído en mercados líquidos | **RECHAZADA-POR-COSTE** |
| H004 vol premium | — | — | — | — | fuera por DATOS (opciones) |
| AMT / volume profile | alto (intradía) | alto | — | — | fuera por DATOS (intradía; panel EOD) |

## Casos resueltos explícitamente

**H002 (carry) — RECHAZADA. Motivo PRINCIPAL: concentración, no coste.** Evidencia
propia medida (portafolio long top-3/short bottom-3, vol-inversa, 8% vol): **Sharpe
bruto (spot+carry) = 0.495, neto = 0.282** — el **mejor resultado del proyecto** (trend
daba ~0.03-0.08). Muere por **umbral, no por falsador** (0.282 > 0.2, pero < 0.4).
La razón de rechazo NO es el coste sino la **concentración**: N_eff FX 3.41, casi todo
**short-JPY — no es una cartera, es una posición**. La prima de carry es compensación
por riesgo de CRASH, y un crash del yen es exactamente lo que una barrera absorbente
no perdona → descalificante contra el objetivo de P(pasar challenge), con independencia
del Sharpe. Ese 0.282 es engañoso: paga por asumir el riesgo de cola que el challenge
castiga. (El coste es secundario: su gross 0.495 < 0.64 requerido de todos modos.)

**H005 (reversión corto plazo) — RECHAZADA-POR-COSTE.** Duty ~100% y turnover 50-100×
→ requerido ~0.78 (0.64 + ~0.14 de spread por la rotación). La reversión a la media a
nivel índice reporta brutos ~0.3-0.5, muy por debajo. Cerrada formalmente sin correr.

**H006 (intermarket/macro) — RECHAZADA-POR-COSTE.** Price-based, siempre-en-mercado
(duty ~100% → requerido 0.64). El lead-lag entre mercados líquidos está documentado
como decaído; sin evidencia de bruto ≥ 0.64. Además compite contra todos los que
tienen precios (filtro 4 débil). Se cierra salvo que aparezca un diseño de bajo duty.

**H004 (vol premium) y AMT/volume profile — fuera por DATOS.** H004 necesita opciones;
AMT/volume profile necesita intradía. Nuestro panel es OHLC diario spot/CFD.

## Conclusión — cuántas mueren sin correrse

**Las TRES hipótesis price-based vivas (H002, H005, H006) mueren por el filtro #6**,
más dos fuera por datos (H004, AMT). Es un resultado estructural, no de mala suerte:
**todo lo price-based sobre nuestro setup EOD/high-duty muere en el suelo de costes.**

El camino que queda no es otra hipótesis de precio. Es una fuente **NO-de-precio** y
de **bajo duty cycle** (para bajar el margen requerido a ~0.42-0.45). Eso es
exactamente COT (posicionamiento, se opera sólo en extremos) → Bloque 2.
