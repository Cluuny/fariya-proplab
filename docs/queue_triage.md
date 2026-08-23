# Triaje de la cola por filtro #6 (coste) — semana 9

El suelo lo domina el margen, proporcional al **duty cycle** (fracción de días con
posición abierta). Criterio de admisión, POR ENCIMA del orden de la cola:

    sharpe_bruto_requerido ≈ 0.24 × duty_cycle + 0.40   (costs_model.sharpe_bruto_requerido_duty)
    duty 100% → 0.64   ·   50% → 0.52   ·   20% → 0.45   ·   10% → 0.42

**Trampa (no es magia):** el bruto de una estrategia de duty bajo se mide sobre TODA
la serie, flat days incluidos. Un efecto grande en 20 días/año se diluye al
anualizar: `Sharpe_whole ≈ Sharpe_activo × √duty`. Para cumplir el requerido con duty
bajo hace falta `Sharpe_activo ≥ (0.24·duty+0.40)/√duty`. El ahorro de margen (lineal)
y la dilución (√duty) se compensan en parte. Duty bajo ayuda, pero exige edge activo
fuerte.

## Tabla de triaje (entradas vivas)

| Hipótesis | duty | turnover | bruto requerido | bruto plausible | veredicto |
|---|---|---|---|---|---|
| **H002** carry | 100% | ~9× | **0.64** | **0.495** (medido, gross spot+carry) | **RECHAZADA-POR-COSTE** |
| **H005** reversión corto plazo | ~100% | 50-100× | **0.78** (0.64 + spread de rotación) | 0.3-0.5 (literatura índices) | **RECHAZADA-POR-COSTE** |
| **H006** intermarket/macro | ~100% (price-based, siempre-en) | medio | ~0.64 | sin evidencia de bruto alto; lead-lag decaído en mercados líquidos | **RECHAZADA-POR-COSTE** |
| H004 vol premium | — | — | — | — | fuera por DATOS (opciones) |
| AMT / volume profile | alto (intradía) | alto | — | — | fuera por DATOS (intradía; panel EOD) |

## Casos resueltos explícitamente

**H002 (carry) — RECHAZADA-POR-COSTE.** Pasó el cribado A.4 (carry 2.17% vs margen
1.10%) porque esa pregunta era carry vs MARGEN. El filtro #6 pregunta carry vs
MARGEN + UMBRAL. Evidencia propia medida (portafolio long top-3/short bottom-3,
vol-inversa, 8% vol): **Sharpe bruto (spot+carry) = 0.495, neto = 0.282.** El bruto
0.495 < 0.64 requerido → el neto (~0.28) no alcanza el umbral 0.40. Es el mejor neto
del proyecto (trend daba ~0.03-0.08), pero estructuralmente corto.
Riesgo de concentración registrado: **N_eff FX 3.41, casi todo short-JPY — no es una
cartera, es una posición.** La prima de carry es compensación por riesgo de crash, y
un crash del yen es exactamente lo que una barrera absorbente no perdona: ese 0.282
neto es engañoso (P(pasar challenge) lo castigaría por la cola). Doble razón para no
correrla.

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
