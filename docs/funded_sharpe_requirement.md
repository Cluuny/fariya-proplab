# Curva de Sharpe requerido para el ciclo completo de fondeo

**Fecha:** 2026-08-26. **Modo:** aritmética sobre `src/challenge.py` (el simulador de barrera de la
semana 4), aplicado por primera vez a la pregunta del ciclo completo. Fuente:
`scripts/funded_sharpe_requirement.py`. NO requiere datos nuevos ni suscripción.

**LA RESPUESTA EN UNA LÍNEA (D4):** el Sharpe **BRUTO** mínimo para pasar, ganar y sobrevivir es
**~0.5** para una probabilidad de éxito del **50%** (una moneda al aire) y **~0.8** para **70-80%**
(ingreso fiable) — y el mejor bruto que el programa MIDIÓ (H002 **0.495**) apenas roza el umbral del
50% y **no es desplegable** (murió por concentración); trend (0.37) e industria (0.32) quedan por
**DEBAJO**. El negocio de fondeo exige justo el Sharpe que el terreno no da.

## Modelo (honesto, con sus supuestos)

- El Sharpe barrido es **BRUTO** (para contrastar directo con lo medido). El NETO que mueve la
  cuenta = bruto − drag de swap.
- **Swap DIRECCIONAL** (no el placeholder unsigned): en un libro long/short diversificado el carry
  con signo ~se cancela (hallazgo del programa), así que el drag residual es el **margen
  unidireccional** del broker: `_MARGIN_FX·BROKER_MARGIN_MULT·(365/261)` ≈ **0.42 bp/d** (mult 1.0)
  / **0.63** (mult 1.5) → ~1.1% / 1.6% anual de drag sobre exposición ~1.
- Retornos sintéticos con momentos EXACTOS (estandarizados), bootstrapeados en bloques (block 20)
  por `challenge.py`, 10.000 caminos, horizonte 756 d/fase, semilla 12345.
- **Guards respetados:** `p_unresolved>5% → días=nan` (horizonte insuficiente, se ve a vol baja);
  `optimal_leverage=None` (objetivo no definido); leverage fijo 1.0 (barremos VOL, no leverage).
- Reglas de la firma: fase 1 +10%, fase 2 +5%, límite diario 5%, drawdown estático 10%, ciclo de
  payout 21 d. Cuenta $50k, split 90%, escalado $50k→$150k→$300k por consistencia, cuota ~$300.

**Caveats (todos empujan el requerido hacia ARRIBA, no abajo):** (1) el modelo de fase fondeada NO
resetea el balance entre ciclos (limitación documentada en `challenge.py`) → P(quemar) es
OPTIMISTA; aun así el cuello es PASAR, no sobrevivir. (2) retornos normales sin colas gordas ni
autocorrelación → P(pasar) real sería MENOR. (3) la capa económica usa supuestos marcados (cuota
$300, split 90%). Bajo supuestos más realistas el Sharpe requerido sólo SUBE.

## D1. P(pasar) / P(quemar) / P(éxito) por Sharpe y vol (mult 1.0)

| S bruto | vol | P1 | P2 | P(pass cond) | días | P(burn 4/8/12) | ret neto % | payout/año $ | **P(éxito)** |
|---|---|---|---|---|---|---|---|---|---|
| 0.0 | 8% | 0.37 | 0.60 | 0.26 | nan | 0/0/0 | −1.1 | −476 | **0.26** |
| 0.2 | 8% | 0.46 | 0.68 | 0.38 | nan | 0/0/0 | 0.5 | 244 | **0.38** |
| 0.3 | 8% | 0.53 | 0.72 | 0.44 | nan | 0/0/0 | 1.3 | 604 | **0.44** |
| 0.5 | 8% | 0.63 | 0.79 | 0.58 | nan | 0/0/0 | 2.9 | 1324 | **0.58** |
| 0.8 | 8% | 0.81 | 0.90 | 0.82 | nan | 0/0/0 | 5.3 | 2404 | **0.82** |
| 1.0 | 8% | 0.86 | 0.92 | 0.84 | 475 | 0/0/0 | 6.9 | 3124 | **0.84** |
| 1.5 | 8% | 0.95 | 0.96 | 0.93 | 345 | 0/0/0 | 10.9 | 4924 | **0.93** |

(vol 6% y 10% en el script; el patrón es el mismo, con vol alta ayudando a Sharpe bajo —más
absorción vía ruido— y perjudicando a Sharpe alto —el ruido diluye el edge.)

**Hallazgo estructural: P(quemar) ≈ 0 en todo el barrido.** El drawdown estático (10%) está lejos
respecto a la vol de una ventana de payout de 21 días → **el cuello NO es sobrevivir, es PASAR.**
P(éxito) ≈ P(pasar ambas fases); el término de supervivencia a 12 ciclos apenas lo mueve.

## D1b. Sensibilidad BROKER_MARGIN_MULT 1.5 (vol 8%)

Subir el margen del broker 1.0→1.5 (prop firm peor que afterprime/FTMO) baja P(éxito) ~0.02-0.06
por Sharpe (más drag → menos deriva neta): S=0.5 0.58→0.53, S=0.8 0.82→0.70. Desplaza el umbral de
70% de 0.8 a 1.0. El margen importa, pero no cambia el orden de magnitud del requerido.

## D2. Sharpe BRUTO mínimo para P(éxito) ≥ umbral

| vol | mult | P(éxito)≥50% | ≥70% | ≥80% |
|---|---|---|---|---|
| 6% | 1.0 | **0.5** | 0.8 | 0.8 |
| 8% | 1.0 | **0.5** | 0.8 | 0.8 |
| 8% | 1.5 | **0.5** | 1.0 | 1.0 |
| 10% | 1.0 | **0.5** | 0.8 | 1.5 |
| 10% | 1.5 | **0.5** | 1.0 | 1.5 |

**Robusto: ~0.5 para el 50%, ~0.8 para el 70-80% (hasta 1.0-1.5 con margen alto o vol alta).**

## D3. La aritmética del dinero (vol 8%, mult 1.0, split 90%)

| S bruto | ret neto % | payout/mo $50k | payout/mo $150k | payout/mo $300k | #cuentas p/ $1k/mo | #cuentas p/ $2.5k/mo | cuotas/año $ |
|---|---|---|---|---|---|---|---|
| 0.3 | 1.3 | 50 | 151 | 302 | 4 | 9 | 675 |
| 0.5 | 2.9 | 110 | 331 | 662 | 2 | 4 | 520 |
| 0.8 | 5.3 | 200 | 601 | 1202 | 1 | 3 | 368 |
| 1.0 | 6.9 | 260 | 781 | 1562 | 1 | 2 | 359 |
| 1.5 | 10.9 | 410 | 1231 | 2462 | 1 | 2 | 322 |

(#cuentas calculado sobre la cuenta escalada al máximo, $300k. Cuotas/año ≈ cuota × (1/Pcond) ×
(1 + reintentos por quema) — aproximación marcada; a Sharpe bajo las cuotas se disparan porque
fondearse cuesta más intentos.) A Sharpe 0.3 hacen falta **9 cuentas de $300k** para $2.5k/mo; a
Sharpe 0.8, **3**. Por debajo de ~0.3 el payout no cubre ni las cuotas (a S=0.0 el drag de swap da
retorno NEGATIVo → ∞ cuentas, sólo quemas).

## D5. Contraste contra lo que el programa MIDIÓ

| referencia (bruto) | valor | P(éxito) a vol 8% | ¿alcanza el negocio? |
|---|---|---|---|
| **Requerido P(éxito)≥50%** | **0.5** | 0.50 (moneda al aire) | umbral mínimo |
| **Requerido P(éxito)≥70-80%** | **0.8** | 0.82 | ingreso fiable |
| H002 carry (el MEJOR del proyecto) | 0.495 | ~0.58 | roza el 50% — **pero murió por concentración (N_eff 3.41), no desplegable** |
| H007-A trend | 0.370 | ~0.50 | justo la moneda al aire; payout ~$50-110/mo, no es negocio |
| Industria CTA (bruto de comisiones) | ~0.32 | ~0.45 | **por DEBAJO del umbral del 50%** |

**El mínimo requerido está POR ENCIMA de lo alcanzable desplegable.** El único número medido que
alcanza el umbral del 50% (H002, 0.495) no es operable (concentración short-JPY). Lo desplegable
—trend 0.37, industria 0.32— queda en o por debajo de la moneda al aire, con un payout que no
cubre las cuotas. Para un ingreso fiable (70-80%) hace falta ~0.8, más del doble de lo alcanzable.

## Conclusión

Esta es la MISMA pared del programa, vista desde el lado del PAYOUT en vez del suelo de costes: el
negocio de fondeo exige un Sharpe bruto ~0.5 (moneda al aire) a ~0.8 (fiable), y el terreno
accesible da 0.32-0.37 desplegable. Coherente con el cierre por amplitud (`docs/terrain_breadth.md`,
`docs/program_verdict.md` §1.7-1.8): no es que falte una estrategia más, es que el Sharpe que el
negocio necesita está por encima del que la amplitud del terreno permite generar. Confirma el
cierre desde una tercera dirección independiente. (Sin contratar nada, sin pre-registrar nada.)
