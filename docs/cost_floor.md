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
