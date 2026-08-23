# Expansión de universo — ingesta y amplitud efectiva (Bloque 2)

**Fecha:** 2026-08-22 · Universo operable **9 → 18** (opción (a): limpio + live).

## Instrumentos añadidos (9)
Cruces FX (decorrelan del factor USD): **EURJPY, GBPJPY, AUDJPY, EURAUD, GBPAUD,
EURCHF**. Metal: **XAGUSD** (plata). Índices: **US30** (Dow), **HK50** (Hang Seng).
Ingeridos a `data/clean` vía `loaders`; cobertura y anomalías en
`data/quality_report.md` (todos coinciden con la auditoría del Bloque 1).

## Amplitud efectiva — la métrica de progreso (no el conteo)

`N_eff = (Σλ)² / Σλ²` sobre los autovalores de la matriz de correlación de
retornos diarios (participation ratio). Sobre 1945 días comunes (2017+):

| | N | **N_eff** | N_eff/N |
|---|---|---|---|
| ANTES | 9 | **3.73** | 0.41 |
| DESPUÉS | 18 | **5.20** | 0.29 |

**Ganancia: +1.47 apuestas independientes (×1.39).** Duplicar el conteo (9→18) sólo
sumó ~1.5 de amplitud efectiva: los cruces FX son en buena parte combinaciones de
los majors, así que aportan menos de 1 cada uno. Por Grinold-Kahn (IR ≈ IC·√BR), el
**techo de Sharpe sube ×1.18** (~18%) — real pero modesto. Reproducir:
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

## Recomendación

- **Quitar US30**: es el único con aporte **negativo** — está tan correlacionado con
  SPX500 que baja la amplitud efectiva. Mantener SPX500 como el representante de
  equity-US large-cap. Universo quedaría en **17** con N_eff ligeramente mayor.
- **AUDJPY** es marginal (+0.05); se puede conservar (es un cruce genuino) o quitar
  si se prioriza limpieza. Recomendación: conservar por ahora.
- Los diversificadores reales fueron **EURCHF, GBPAUD y HK50** — validan la tesis del
  Bloque 1 (romper la dominancia USD + geografía).

## Conclusión

La expansión hizo su trabajo pero con la lección honesta que la métrica correcta
revela: **+1.5 de amplitud efectiva, no +9**. El techo de Sharpe sube ~18%. Los gaps
estructurales (rates, energía) siguen siendo el camino a datos pagos si se quiere
más amplitud real. Próximo: pre-registrar H005 (reversión a la media) y una H007 de
trend sobre este universo ampliado (segunda mirada al efecto de H001, con su propio
falsador).
