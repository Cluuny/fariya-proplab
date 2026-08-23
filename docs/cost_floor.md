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
