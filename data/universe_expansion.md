# Expansión de universo — ingesta y amplitud efectiva (Bloque 2)

**Fecha:** 2026-08-22 · Universo operable **9 → 17** (opción (a) limpio+live, menos
US30). US30 (Dow) se retiró tras medir amplitud (change `universe-trim-us30`): es la
misma exposición que SPX500 → paga spread dos veces por la misma posición (fricción
pura). Quitarlo **subió** N_eff (5.20 → 5.32), confirmando que era redundante.

## Instrumentos añadidos (8 netos)
Cruces FX (decorrelan del factor USD): **EURJPY, GBPJPY, AUDJPY, EURAUD, GBPAUD,
EURCHF**. Metal: **XAGUSD** (plata). Índice: **HK50** (Hang Seng). Ingeridos a
`data/clean` vía `loaders`; cobertura y anomalías en `data/quality_report.md` (todos
coinciden con la auditoría del Bloque 1).

## Amplitud efectiva — la métrica de progreso (no el conteo)

`N_eff = (Σλ)² / Σλ²` sobre los autovalores de la matriz de correlación de
retornos diarios (participation ratio). Sobre 1945 días comunes (2017+):

| | N | **N_eff** | N_eff/N |
|---|---|---|---|
| ANTES | 9 | **3.73** | 0.41 |
| DESPUÉS (con US30) | 18 | 5.20 | 0.29 |
| **DESPUÉS (sin US30)** | **17** | **5.32** | 0.31 |

**Ganancia: +1.59 apuestas independientes (×1.43).** Casi duplicar el conteo sólo
sumó ~1.6 de amplitud efectiva: los cruces FX son en buena parte combinaciones de
los majors, así que aportan menos de 1 cada uno. Por Grinold-Kahn (IR ≈ IC·√BR), el
**techo de Sharpe sube ×1.19** (~19%) — real pero modesto. (Ver la limitación de
N_eff como métrica en `docs/breadth-lessons.md`.) Reproducir:
`uv run python scripts/effective_breadth.py`.

## Aporte marginal por instrumento (N_eff de los 9 + ese uno)

| instrumento | Δ N_eff | lectura |
|---|---|---|
| EURCHF | **+0.51** | CHF es una divisa distinta (régimen SNB) — el mejor diversificador |
| GBPAUD | +0.41 | cruce no-USD, no-JPY |
| HK50 | **+0.39** | Hang Seng — geografía asiática nueva |
| EURJPY | +0.31 | |
| EURAUD | +0.25 | |
| GBPJPY | +0.24 | |
| XAGUSD | +0.21 | plata (correlaciona con oro) |
| AUDJPY | +0.05 | casi redundante (spanned por AUD/JPY majors) |
| **US30** | **−0.13** | **Dow reduce la amplitud: ~redundante con SPX500, sólo engorda el eigen-vector de equity-US** |

## Decisión aplicada

- **US30 retirado** (change `universe-trim-us30`). Razón real: **fricción**, no el
  −0.13 (que está en el ruido de la métrica) — US30 y SPX500 son la misma exposición
  equity-US, así que en sizing vol-inversa se paga spread dos veces por la misma
  posición. Quitarlo subió N_eff (5.20 → 5.32), confirmando la redundancia. Universo
  activo = **17**.
- **AUDJPY conservado** (+0.05): aporta poco pero no cuesta, y en carry el cruce
  AUD/JPY podría importar.
- Los diversificadores reales fueron **EURCHF, GBPAUD y HK50** — validan la tesis del
  Bloque 1 (romper la dominancia USD + geografía). Pero ver `docs/breadth-lessons.md`:
  los cruces FX son recombinaciones de los majors (cero información nueva), así que
  el +1.6 de N_eff **sobreestima** la ganancia informativa real.

## Conclusión

La expansión hizo su trabajo pero con la lección honesta que la métrica correcta
revela: **+1.5 de amplitud efectiva, no +9**. El techo de Sharpe sube ~18%. Los gaps
estructurales (rates, energía) siguen siendo el camino a datos pagos si se quiere
más amplitud real. Próximo: pre-registrar H005 (reversión a la media) y una H007 de
trend sobre este universo ampliado (segunda mirada al efecto de H001, con su propio
falsador).
