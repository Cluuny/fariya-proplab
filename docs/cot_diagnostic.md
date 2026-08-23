# Diagnóstico condicional de COT (cribado, NO una hipótesis)

Los datos ya ingeridos responden la pregunta antes de construir nada. Se condiciona el
retorno futuro (1/2/4 semanas) sobre el percentil rodante (3 años) del neto de
especuladores y se mide el **Sharpe activo** del subconjunto en extremos, **fadeando**
(mecanismo: specs extremos largos → retorno futuro negativo). No consume intentos, no
toca el holdout, no requiere ficha. Reproducir: `uv run python scripts/cot_screen.py`.

## Expectativa comprometida (escrita ANTES de correr)

El Sharpe activo caerá en **0.4-0.8**, por debajo del listón. El efecto COT está
documentado como real pero débil, y la alta autocorrelación (0.85-0.98) implica pocas
observaciones independientes → IC ancho.

## Criterio de decisión (comprometido antes de correr)

- Sharpe activo **≥ 1.1** → H008 se pre-registra y se construye.
- Sharpe activo **0.7-1.1** → zona marginal, decisión explícita documentada.
- Sharpe activo **< 0.7** → COT muere SIN pre-registro, como H005 y H006.

(El listón ~1.1 sale de `costs_model.sharpe_activo_requerido` a duty ~20%: `0.40/√duty
+ 0.245`. Duty bajo SUBE el listón, no lo baja — ver la corrección en `cot_coverage.md`.)

## Resultado — Sharpe activo (fade, holding 2 semanas)

**Umbral p10/90:**

| inst | n episodios | Sharpe activo | IC95 (bootstrap por episodio) | signo del mecanismo |
|---|---|---|---|---|
| EURUSD | 49 | −0.41 | [−1.95, +1.03] | ✗ (specs acertaron) |
| GBPUSD | 71 | −1.25 | [−2.18, −0.14] | ✗ |
| AUDUSD | 60 | −1.06 | [−2.05, +0.04] | ✗ |
| USDJPY | 82 | −0.36 | [−1.51, +0.82] | ✗ |
| USDCAD | 63 | **+1.59** | [+0.43, +2.78] | ✓ |
| XAUUSD | 62 | −0.40 | [−1.64, +0.79] | ✗ |
| XAGUSD | 118 | +0.23 | [−0.75, +1.10] | ✓ |
| SPX500 | 45 | +0.97 | [−0.26, +2.08] | ✓ |
| **AGRUPADO** | **454** | **−0.02** | **[−0.42, +0.34]** | — |

**Por horizonte (agrupado, p10/90):** 1s = −0.29 [−0.87, +0.25] · 2s = −0.02 [−0.42,
+0.34] · 4s = −0.04 [−0.34, +0.27]. **Umbral p5/95, 2s:** agrupado −0.14 [−0.58, +0.27].

## Lectura

1. **Sharpe activo agrupado ≈ 0** en todos los horizontes y umbrales, con IC que
   **cruza 0**. No hay edge, mucho menos el ~1.1 requerido.
2. **El signo del mecanismo FALLA en 5 de 8** (EURUSD, GBPUSD, AUDUSD, USDJPY, XAUUSD):
   ahí los specs extremos **acertaron** (momentum, no reversión) — lo contrario de la
   tesis. Sólo USDCAD, plata y SPX500 fadean con signo correcto, y sólo USDCAD supera
   el listón individualmente (probable falso positivo por multiplicidad: 8 instrumentos).
3. **No es falta de poder.** n episodios 43-118 por instrumento (>30) y 350-489
   agrupado; el bootstrap por episodio da un IC razonablemente estrecho alrededor de 0.
   Es un cero de verdad, no un "no se puede saber".

## Veredicto — COT MUERE sin pre-registro

Sharpe activo agrupado −0.02 (2s) **< 0.7** → por el criterio comprometido, **COT no se
pre-registra**, como H005 y H006. El resultado es incluso **más débil que la
expectativa comprometida** (0.4-0.8): no es débil-pero-positivo, es ~cero y con el
signo del mecanismo roto en la mayoría de instrumentos.

**Qué NO invalida esto:** el argumento de fondo de COT (información NO-de-precio) sigue
siendo el correcto — pero a resolución SEMANAL/EOD y sobre estos 8 instrumentos, el
efecto de reversión de posicionamiento no está. Podría existir a otra frecuencia, con
otra construcción de señal (no fade simple), o en instrumentos que no tenemos. Nada de
eso se explora sin una razón nueva: por ahora, COT no pasa el cribado. **H008 no se
escribe.**
