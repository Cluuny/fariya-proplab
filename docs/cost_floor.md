# El suelo de costes — herramienta de decisión (Bloque A)

Cuatro mediciones (H001-A/B, H007-A/B) dicen que el bruto de trend vive en 0.23-0.37
de Sharpe y que **los costes se comen ~88% del retorno bruto**. Este documento
convierte eso en un filtro previo a correr, no en una observación. Herramienta:
`src/costs_model.py`. Perfil recomendado al final (tras el Bloque B).

## A.1 — Descomposición del coste (números medidos)

Anual, como fracción del NAV. Medido en corridas reales con el swap direccional
histórico corregido:

| Componente | Fórmula | por unidad de | H001-A (g=1.71, t=8.8) | H007-B (g=1.94, t=10.9) |
|---|---|---|---|---|
| **margen** | `0.42 bp/día × gross × 261` | GROSS | 1.96%/año | 2.20%/año |
| spread+slippage | `1.5 bp × turnover` | TURNOVER | 0.13%/año | 0.16%/año |
| carry | `E[carry·w]` (signed) | — | +0.19%/año | +0.25%/año |
| **coste total** | margen + spread − carry | | **1.91%/año** | **2.11%/año** |
| bruto medido | | | 2.16%/año | 2.04%/año |

**El margen es ~92% del coste.** Verificación del modelo (`costs_model.annual_cost`):
a gross 1.71, turnover 8.8 → 1.94%/año (medido 1.91%). El margen escala LINEAL con
gross; el spread con turnover; el carry es pequeño en trend (~+0.2%/año, no compensa).

## A.2 — Sharpe bruto requerido

`costs_model.sharpe_bruto_requerido(vol, gross, turnover, umbral)`:
`net_sharpe = gross_sharpe − coste/vol` → `requerido = umbral + coste/vol`.

Con los parámetros actuales (vol 8%, gross 1.7, turnover 9):
- **break-even** (net 0): coste/vol = 1.94%/8% = **0.24**
- **requerido** (net > 0.4): 0.24 + 0.40 = **0.64**

El trend real entrega bruto 0.23-0.37 → estructuralmente por debajo del 0.64 requerido.
Por eso murió tres veces. **No es mala suerte: es el suelo de costes.**

## A.3 — Filtro de admisión #6 (añadir al protocolo del documento maestro)

> **Filtro #6 — Suelo de costes.** Ninguna hipótesis entra a la cola sin una
> estimación PREVIA de su gross y turnover esperados, y del Sharpe bruto requerido
> que implican (`costs_model.sharpe_bruto_requerido`). Si el bruto requerido excede
> lo que la literatura reporta para esa familia, se descarta SIN correrla.

Aplicado retroactivamente a la cola:

- **H005 (reversión a la media, corto plazo):** turnover esperado **50-100×/año**
  (holding de días). Spread solo: 1.5 bp × 75 ≈ **1.1%/año**, ENCIMA del margen.
  Coste total ~3%/año → break-even ~0.38, requerido (net 0.4) **~0.78**. Necesita un
  bruto MAYOR que trend. La reversión a la media a nivel índice raramente reporta
  brutos así de altos netos de rotación → **candidata a descarte por filtro #6**
  salvo que se diseñe explícitamente de bajo turnover (banda muerta amplia).
- **H002 (carry):** ver A.4 — pasa el cribado.

## A.4 — Cribado de H002 (carry) — sin pre-registro, sin comprometer nada

Portafolio de carry estático (long top-3 / short bottom-3 por carry histórico,
vol-inversa, gross 1), sobre las 11 divisas (majors + cruces):

| Número | Valor |
|---|---|
| **E[carry·w] anualizado** | **+2.17%/año** |
| coste de margen (gross 1) | 1.10%/año |
| → carry vs margen | **carry SUPERA el margen ~2×** (+1.07%/año antes de spread) |
| amplitud efectiva FX (N_eff) | 3.41 (universo); la apuesta de carry está concentrada en **short-JPY** (~1-2 bets independientes) |

**EXPECTATIVA COMPROMETIDA (escrita antes de correr): el carry no supera el margen,
H002 no pasa. → REFUTADA.** El carry capturable (2.17%/año) es ~2× el margen
(1.10%/año), y el ratio es invariante al escalado (ambos escalan con gross). Por la
aritmética del cribado, **H002 SÍ pasa** — no muere por costes.

Caveats honestos (no invalidan el cribado, sí acotan la expectativa):
- **Concentración**: long USDJPY+GBPJPY+AUDJPY+EURJPY es la misma apuesta (corto JPY);
  el universo tiene ~1-2 apuestas de carry independientes, no 11 (N_eff FX 3.41, y el
  carry-bet es más concentrado aún). Amplitud efectiva baja → techo de Sharpe bajo.
- **Riesgo de crash**: el Sharpe del componente SPOT del portafolio de carry es solo
  +0.065 — el carry se cobra en calma y se devuelve en crashes (forward premium
  puzzle). El +2.17% es acumulación de carry, no retorno ajustado por riesgo.

**Conclusión A.4:** H002 pasa el filtro #6 (carry > margen) y merece pre-registro
formal (con su estimación de gross/turnover y sus caveats de concentración/crash),
a diferencia de H005. NO se pre-registra ni se corre todavía.

---

# Las dos palancas que bajan el suelo (Bloque B)

El suelo NO es fijo — pero de las dos palancas candidatas, **ninguna funciona como se
esperaba**. Reproducir: `scripts/cost_levers.py`.

## B.1 — Barrido de gross exposure → NO es palanca (Sharpe neto invariante)

Señal tsmom sobre los 17, escalando los pesos a gross objetivo G:

| G | Sharpe bruto | Sharpe neto |
|---|---|---|
| 0.50 → 2.50 (todos) | +0.229 (plano) | −0.145 (plano) |

**Expectativa del reviewer (neto con máximo interior): REFUTADA.** El neto es TAN plano
como el bruto. Razón: margen (∝gross), spread (∝turnover∝gross), carry (∝gross), retorno
bruto (∝gross) Y la vol (∝gross) escalan TODOS linealmente. Entonces
`neto = bruto − coste/vol`, y `coste/vol` es invariante al escalado → no hay óptimo
interior. **El gross exposure NO baja el suelo** (dado que la estrategia ya apunta a una
vol objetivo). Subir diversificación sí ayudaría al bruto (√N_eff), pero eso es cambiar
la señal, no escalar el gross.

## B.2 — Horizonte de holding → sólo recorta el spread (despreciable)

| Rebalanceo | turnover | margen | spread | Sharpe neto |
|---|---|---|---|---|
| mensual | 10.9× | 2.20% | 0.16% | −0.008 |
| bimestral | 8.4× | 2.23% | 0.13% | −0.019 |
| trimestral | 6.3× | 2.16% | 0.10% | −0.047 |

**El margen es INVARIANTE al holding** (se paga cada día que se mantiene, sin importar la
frecuencia de rebalanceo); alargar el holding sólo baja el spread (0.16%→0.10%, ~0.06%),
despreciable frente al margen de 2.2%. Y el neto empeora (la señal de trend pierde
frescura). **El horizonte de holding NO baja el suelo de forma material.**

## Respuesta combinada — ¿qué perfil supera el suelo?

El suelo está DOMINADO por el margen (~2.2%/año, ~92% del coste), que es
`margen = margin_bp/día × (gross promedio sobre TODOS los días) × 261`. Es irreducible
para una estrategia que está **siempre en el mercado**. Las dos palancas obvias fallan:
gross scaling (neto invariante) y holding largo (sólo recorta el spread). Por tanto, el
perfil que tiene la mejor probabilidad de superar el suelo NO es "más diversificado a más
gross" ni "holding más largo", sino:

1. **Edge bruto mucho mayor** — Sharpe bruto > **0.64** (break-even 0.24 + umbral 0.40).
   El trend real (0.23-0.37) no llega; hace falta una familia con más señal.
2. **Duty cycle bajo** — estar FLAT la mayor parte del tiempo. El margen se paga sólo
   mientras se mantiene posición, así que el gross PROMEDIO-sobre-todos-los-días es lo que
   cuenta. Una estrategia activa el ~19% de los días (como TOM) paga ~1/5 del margen de
   una always-in. (TOM murió igual por bruto débil, pero el mecanismo es real y es la
   única forma estructural de bajar el margen.)

**Criterio de selección de la próxima hipótesis (POR ENCIMA del orden de la cola):**
priorizar hipótesis con (a) bruto reportado alto en la literatura (>0.64 tras el filtro
#6) y/o (b) bajo duty cycle (señal selectiva, flat la mayor parte del tiempo). H002
(carry) tiene bruto/carry favorable (pasó el cribado) pero es always-in (duty cycle alto)
y concentrado — su margen será alto; su pre-registro debe estimar gross y duty cycle y
pasar el filtro #6 con esos números.

---

## Suelo de costes INTRADÍA — cambia de régimen (change research-pipeline-intraday)

El modelo de arriba es **swing**: el coste lo domina el **mantener** (margen diario). En
**intradía lo domina el ROTAR** — el margen es despreciable y el coste es comisión +
spread por operación × frecuencia. `costs_model.sharpe_bruto_requerido_intraday`:

    costo_anual = trades_por_dia × 252 × (comision_rt + spread_$) / notional
    bruto_requerido = umbral(0.40) + costo_anual / vol_objetivo(8%)

**Calibración** (specs CONTRACTUALES de CME —tick/point value son definiciones estables—
+ comisión IBKR ~$4.20 round-trip; `notional` al nivel de precio ~2026-08, RECALCULAR a
precio corriente antes de decidir). `spread_$` = 1 tick del front líquido.

| contrato | tick $ | notional $ | coste/round-trip | coste por 1 trade/día |
|---|---|---|---|---|
| ES | 12.50 | 300 000 | $16.70 | **1.40%/año** |
| NQ |  5.00 | 400 000 | $9.20  | 0.58%/año |
| CL | 10.00 |  75 000 | $14.20 | **4.77%/año** |
| GC | 10.00 | 240 000 | $14.20 | 1.49%/año |

### Tabla de referencia (ES, vol 8%)

| trades/día | coste anual aprox | bruto requerido (vol 8%) |
|---|---|---|
| 0.05 (swing, ~12/año) | 0.07% | 0.41 |
| 1 | 1.40% | 0.58 |
| 2 | 2.81% | 0.75 |
| 5 | 7.01% | 1.28 |
| 20 | 28.06% | 3.91 |

### La advertencia principal

Referencia de contraste: el **CFD swing** tenía coste **1.96%/año** y requerido **0.64**, y
**mató seis hipótesis**. ¿A partir de cuántos trades/día el coste intradía SUPERA ese
1.96%?

| contrato | round-trips/día que igualan el 1.96% del margen CFD |
|---|---|
| **CL** | **0.41** (¡menos de 1 trade/día ya es más caro que el CFD!) |
| GC | 1.31 |
| **ES** | **1.40** |
| NQ | 3.38 |

**Por encima de ~1.4 round-trips/día en ES (0.4 en CL), el intradía es MÁS caro que el
suelo que ya mató seis hipótesis** — y el bruto requerido crece linealmente con la
frecuencia. Cualquier hipótesis intradía tiene que reportar un bruto muy por encima de
0.64 para justificar rotar; ése es el listón que la estación 3 le aplica automáticamente.

---

## Suelo de costes CRIPTO — Binance USDⓈ-M perpetuos (change crypto-cost-model)

Régimen distinto otra vez: cripto opera **24/7 (365 días/año)**, la comisión distingue
**maker/taker**, y el **funding es EVITABLE**. `src/crypto/cost_model.py`. Precios VIP0
verificados (binance.com/en/fee/futureFee, 2026-08-24): **maker 0.02%, taker 0.05%**.
Funding cada 8 h en cortes fijos **00:00/08:00/16:00 UTC**, ~0.01%/período (~11%/año si se
mantiene) — **cero si se cierra antes del corte**. Vol y spread MEDIDOS de datos reales
(BTCUSDT 2024-01-02): vol diaria **3.1%** (anual ~60%), spread **0.03 bp** (top of book;
slippage despreciable para tamaños que caben en el mejor nivel).

### Coste por unidad de riesgo (el número del pivote)

Comisión round-trip / vol diaria: **taker 0.032 · maker 0.013** — ambos por debajo del
**MES ~0.063** citado en la racional del pivote (reproduce 0.033 con datos reales). BTC
tiene ~3× la vol con comisiones sólo ~1.6× → coste/riesgo ≈ 0.5×. Éste es el número
COMPARABLE entre vehículos (normalizado por vol).

### Sharpe bruto requerido (vol real ~60%, slippage = spread ≈ 0)

| trades/día | maker | funding en corte | bruto requerido |
|---|---|---|---|
| 1 | 0% (taker) | no | 1.01 |
| 1 | 100% (maker) | no | **0.65** |
| 1 | 100% (maker) | sí | 0.83 |
| 2 | 0% (taker) | no | 1.62 |
| 2 | 100% (maker) | no | **0.89** |
| 5 | 100% (maker) | no | 1.63 |
| 10 | 100% (maker) | no | 2.85 |

(Tabla completa 4×3×2 vía `python -m scripts.crypto_costs`.)

### Comparación honesta contra las referencias del proyecto

- **Coste por unidad de riesgo (la base COMPARABLE):** cripto maker **0.013** / taker
  **0.032** quedan **por DEBAJO** del MES 0.063 → cripto es favorable, tal como dice el
  pivote. Reproducido con datos reales.
- **Nivel absoluto de bruto requerido:** cripto sólo queda a la altura de CFD swing (0.64)
  y MES intradía (0.85) en la esquina **maker + baja frecuencia + funding evitado**: maker
  1 rt/día = **0.65** (≈ CFD 0.64), maker 2 rt/día = **0.89** (≈ MES 0.85). Con **taker** o
  **alta frecuencia** el listón se dispara (taker 2/día 1.62; 10/día 2.85). CAVEAT: las
  referencias 0.64/0.85 se calcularon con la convención simplificada de 8% de vol y NO son
  directamente comparables en nivel; el número comparable es el coste por unidad de riesgo.
- **Las palancas decisivas** (registrar): (1) **maker vs taker** ~halva el premium
  requerido; (2) **evitar funding** ahorra ~0.18 de bruto requerido — la PRIMERA estructura
  de costes del proyecto que **premia estar FUERA del mercado**; (3) la **frecuencia** es
  punitiva (365 días/año). Una estrategia cripto viable casi seguro es **maker, selectiva y
  flat en los cortes de funding** — no un taker de alta frecuencia.
