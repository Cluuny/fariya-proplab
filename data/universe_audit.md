# Auditoría de universo — cobertura real de Dukascopy (Bloque 1)

**Fecha:** 2026-08-22 · **Método:** `scripts/audit_universe.py` sobre descargas d1 de
dukascopy-node (2003-01-01 → 2026-08-17). Mismo criterio que mató a BRENT: **días
hábiles faltantes DENTRO del rango [primer, último] de cada instrumento** (Brent:
~37% faltantes, 166 barras/año → inusable). Se descartan fines de semana como
`loaders.clean`. Umbrales: **KILL > 25%**, CAUTION 10-25%, PASS < 10%.

Dos vistas: **full** (2003→) y **2015+** (la que importa si operamos post-2011; la
sparsidad de CFDs de principios de 2000 infla el número full). `stale_d` = días
desde la última barra (un feed detenido no es operable en vivo).

## Respuestas a las preguntas críticas del plan

- **Renta fija (la pregunta crítica): los CFDs EXISTEN pero la cobertura diaria es
  inusable.** Dukascopy lista `ustbondtrusd` (T-bond US), `bundtreur` (Bund) y
  `ukgilttrgbp` (Gilt UK) — pero: US T-bond sólo **2019-2023** (detenido hace ~959
  días), Bund **52% faltante** y detenido, UK Gilt **sin datos**. → **No hay
  exposición a tasas usable vía Dukascopy daily. Éste es el argumento más fuerte
  para pagar datos de futuros más adelante** — es una limitación estructural, no de
  código.
- **WTI no rescata la energía.** `lightcmdusd` (WTI) tiene **25.8% faltante** — el
  MISMO problema que Brent. No era específico de Brent: los CFDs de energía en
  Dukascopy daily son estructuralmente esparsos (gas natural 40%). Energía: fuera.
- **Los cruces FX son la gran ganancia.** Varios tienen histórico largo y limpio y
  decorrelacionan del factor USD (que hoy domina 5 de nuestros 9): **audjpy, eurjpy,
  gbpjpy, euraud, gbpaud, eurchf** — todos PASS/CAUTION con 0-10% faltante en 2015+.
- **Más índices: mixto.** Dow (`usa30idxusd`) y Hang Seng (`hkgidxhkd`) limpios y al
  día. Pero varios europeos (CAC, IBEX, EuroStoxx, FTSE) y ASX/Russell tienen el
  **feed detenido a fin de 2024/2025** (delistados del daily): usables para backtest
  histórico, NO para operar en vivo sin otra fuente.
- **Metales:** sólo **plata** (`xagusd`, 8.5%, 2003→) es viable además de oro.
  Platino/paladio (`xptcmdusd`/`xpdcmdusd`) sólo devuelven 2026 (162 obs) — sin
  histórico usable. Cobre 34% → KILL.

## Recomendación de universo

### AÑADIR — limpio y al día (live-tradeable), 9 instrumentos → universo 9 ⇒ 18
| símbolo | clase | desde | miss% (full / 2015+) | nota |
|---|---|---|---|---|
| `audjpy` | FX-cross | 2003 | 8.4 / 0.0 | decorrela USD |
| `eurjpy` | FX-cross | 2005 | 9.2 / 0.0 | decorrela USD |
| `gbpjpy` | FX-cross | 2003 | 12.7 / 0.0 | decorrela USD |
| `euraud` | FX-cross | 2003 | 12.7 / 0.0 | decorrela USD |
| `gbpaud` | FX-cross | 2004 | 8.8 / 8.6 | decorrela USD |
| `eurchf` | FX-cross | 2003 | 16.9 / 10.4 | régimen SNB 2015 (anomalía conocida) |
| `xagusd` | Metal | 2003 | 8.5 / 8.6 | plata |
| `usa30idxusd` | Index | 2013 | 7.8 / 8.6 | Dow |
| `hkgidxhkd` | Index | 2013 | 0.0 / 0.0 | Hang Seng (Asia, decorrela) |

### BORDERLINE — añadir con nota (miss 2015+ 11-19%)
| símbolo | clase | miss15% | caveat |
|---|---|---|---|
| `nzdusd` | FX | 17.2 | aún maj-USD |
| `usatechidxusd` | Index | 18.8 | NAS100; correlaciona con SPX |
| `dollaridxusd` | FX-index | 11.4 | DXY = combinación de majors → poca breadth NUEVA |

### RESEARCH-ONLY — histórico limpio pero feed DETENIDO (no live)
`fraidxeur` (CAC, 10% / stale 226d), `eusidxeur` (EuroStoxx, 10% / 227d),
`espidxeur` (IBEX, 0% / 591d), `gbridxgbp` (FTSE, 27% / 226d), `ausidxaud`
(ASX, 27% / 226d), `ussc2000idxusd` (Russell, 25% / 591d). Útiles para backtest,
requieren otra fuente para operar.

### KILL — Brent-like (esparso incluso en 2015+)
`cadjpy` (34.5%), `nzdjpy` (34.5%), `eurgbp` (25.8%), `lightcmdusd` WTI (25.8%),
`coppercmdusd` (34.4%), `gascmdusd` (40.1%).

### Gaps estructurales (ningún ajuste de código los resuelve)
- **Tasas / renta fija**: sin cobertura diaria usable → **argumento para datos pagos de futuros.**
- **Energía**: CFDs esparsos (WTI y Brent y gas). 
- **Platino/paladio**: sin histórico.

## Conclusión

Dukascopy daily lleva el universo **operable en vivo de 9 → ~18** (duplica), con la
ganancia clave en **cruces FX que rompen la dominancia del factor USD** y en
diversificación geográfica (Hang Seng). Sumando los índices europeos delistados se
llega a ~24 para **research histórico**. Los **~25-30 del plan no se alcanzan con un
universo limpio y live**: rates y energía son gaps estructurales. La amplitud
efectiva real (autovalores de la matriz de correlación) se mide en el **Bloque 2** —
es la métrica de progreso, no el conteo bruto de instrumentos.

Reproducir: `uv run python scripts/audit_universe.py --dir <csv_dir>` tras descargar
con dukascopy-node (ver `data/README.md`).
