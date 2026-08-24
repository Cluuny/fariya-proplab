"""decay.py — Bloque B: curva de decaimiento PREDICTIVO del OFI (el cribado que decide).

Para cada horizonte h, se usan bins de tamaño h (el horizonte ES la frecuencia de trading:
1 round-trip por bin). Se regresa:
  - contemporáneo:  return(bin k)      ~ OFI(bin k)   [ya validado a 10s ≈ 0.64]
  - PREDICTIVO:     return(bin k+1)    ~ OFI(bin k)   [EL QUE DECIDE]

Un R² contemporáneo alto es compatible con CERO predictibilidad (el error de H003:
confundir describir con predecir). El cruce con el suelo de costes (Bloque 3) es lo que
convierte esto en una decisión: para cada horizonte se traduce el R² predictivo a un Sharpe
bruto implícito y se compara con el listón requerido a esa frecuencia.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.crypto import cost_model, ofi

SECONDS_PER_YEAR_CRYPTO = 365 * 86400
SECONDS_PER_DAY = 86400

# Horizontes pedidos (segundos).
HORIZONS_S = [1, 5, 10, 30, 60, 300, 900, 1800, 3600]


def _binned(e, t, mid, h_s):
    """OFI (suma de e) y mid (último) por bin de h segundos. Devuelve (ofi[], mid[]).

    `t` viene ORDENADO (ingest lo garantiza), así que los bins son contiguos → se usan
    np.reduceat / bordes de grupo (mucho más rápido que un groupby de pandas sobre 18M)."""
    import numpy as np

    b = t // (h_s * 1000)
    # primer índice de cada bin (b es no-decreciente)
    change = np.empty(len(b), dtype=bool)
    change[0] = True
    np.not_equal(b[1:], b[:-1], out=change[1:])
    first = np.flatnonzero(change)
    ofi = np.add.reduceat(e, first)
    last = np.empty(len(first), dtype=np.intp)
    last[:-1] = first[1:] - 1
    last[-1] = len(mid) - 1
    return ofi, mid[last]


def _corr(x, y):
    import numpy as np
    if x.std() == 0 or y.std() == 0:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def _block_boot_ic(x, y, *, block=50, n_boot=200, cap=120_000):
    """IC (correlación) por block bootstrap (bloques no solapados). Devuelve (lo, hi) 95%.
    Para n muy grande se submuestrea a `cap` (determinista) — la CI apenas cambia y evita
    que los horizontes de 1-5 s (cientos de miles de bins) dominen el cómputo."""
    import numpy as np

    n = len(x)
    if n > cap:                      # submuestra contiguo determinista
        step = n // cap
        x = x[::step][:cap]; y = y[::step][:cap]; n = len(x)
    if n < 2 * block:
        return (float("nan"), float("nan"))
    n_blocks = n // block
    starts_all = np.arange(n_blocks) * block
    offs = np.arange(block)
    ics = np.empty(n_boot)
    for s in range(n_boot):
        pick = (starts_all + s * 7919) % (n - block)
        idx = (pick[:, None] + offs).ravel()
        ics[s] = _corr(x[idx], y[idx])
    lo, hi = np.percentile(ics, [2.5, 97.5])
    return float(lo), float(hi)


@dataclass
class HorizonRow:
    horizon_s: int
    r2_contemp: float
    r2_pred: float
    ic_pred: float
    ic_lo: float
    ic_hi: float
    n_indep: int
    implied_sharpe: float
    implied_sharpe_lo: float
    implied_sharpe_hi: float
    rt_per_day: float
    floor_maker: float
    floor_taker: float
    gap_maker: float          # implied_sharpe − floor_maker (funding evitado)
    gap_taker: float


def _implied_sharpe(ic, h_s):
    """Sharpe bruto anual implícito ≈ IC · √(apuestas/año). Cota superior sin fricción."""
    bets_per_year = SECONDS_PER_YEAR_CRYPTO / h_s
    return ic * (bets_per_year ** 0.5)


def decay_curve(days_events, horizons=HORIZONS_S):
    """`days_events` = ITERABLE que produce (e, t, mid) por día (de ofi.compute_events).
    Se itera UNA vez y se acumulan sólo los pares binned por horizonte (memoria baja:
    máx ~86400/día por horizonte), sin retener los eventos crudos de todos los días a la
    vez. Regresiones contemporánea y predictiva sin cruzar fronteras de día."""
    import numpy as np

    acc = {h: {"xc": [], "yc": [], "xp": [], "yp": []} for h in horizons}
    for e, t, mid in days_events:
        for h in horizons:
            ofi_b, mid_b = _binned(e, t, mid, h)
            if len(mid_b) < 3:
                continue
            ret = np.diff(mid_b) / mid_b[:-1]           # return de cada bin (k desde 1)
            acc[h]["xc"].append(ofi_b[1:]); acc[h]["yc"].append(ret)     # contemporáneo
            acc[h]["xp"].append(ofi_b[1:-1]); acc[h]["yp"].append(ret[1:])  # predictivo k→k+1

    rows = []
    for h in horizons:
        a = acc[h]
        xc, yc = np.concatenate(a["xc"]), np.concatenate(a["yc"])
        xp, yp = np.concatenate(a["xp"]), np.concatenate(a["yp"])
        r2_c = _corr(xc, yc) ** 2
        ic_p = _corr(xp, yp)
        r2_p = ic_p ** 2
        lo, hi = _block_boot_ic(xp, yp)
        n_indep = len(xp)
        rt_day = SECONDS_PER_DAY / h
        floor_m = cost_model.sharpe_bruto_requerido_cripto(rt_day, fraccion_maker=1.0, cruces_funding_por_dia=0)
        floor_t = cost_model.sharpe_bruto_requerido_cripto(rt_day, fraccion_maker=0.0, cruces_funding_por_dia=0)
        sh = _implied_sharpe(ic_p, h)
        sh_lo, sh_hi = _implied_sharpe(lo, h), _implied_sharpe(hi, h)
        rows.append(HorizonRow(
            horizon_s=h, r2_contemp=r2_c, r2_pred=r2_p, ic_pred=ic_p, ic_lo=lo, ic_hi=hi,
            n_indep=n_indep, implied_sharpe=sh, implied_sharpe_lo=sh_lo, implied_sharpe_hi=sh_hi,
            rt_per_day=rt_day, floor_maker=floor_m, floor_taker=floor_t,
            gap_maker=sh - floor_m, gap_taker=sh - floor_t))
    return rows


def verdict(rows) -> dict:
    """Criterio B.4, comprometido antes de correr:
      - algún horizonte con implied_sharpe > listón Y el IC (→sharpe) no cruza el listón → indicio real
      - ninguno supera su listón → ORDER FLOW SE CIERRA (como H005/H006/COT)
      - IC cruza el listón en el mejor horizonte → INDETERMINADO
    Se evalúa contra el listón MAKER + funding evitado (el más barato/favorable)."""
    best = max(rows, key=lambda r: r.gap_maker)
    any_clear = any(r.implied_sharpe_lo > r.floor_maker for r in rows)
    best_crosses = best.implied_sharpe_lo <= best.floor_maker <= best.implied_sharpe_hi
    if any_clear:
        estado = "INDICIO_REAL"
    elif best_crosses:
        estado = "INDETERMINADO"
    else:
        estado = "ORDER_FLOW_CERRADO"
    return {"estado": estado, "mejor_horizonte_s": best.horizon_s,
            "mejor_gap_maker": best.gap_maker, "mejor_implied_sharpe": best.implied_sharpe,
            "mejor_floor_maker": best.floor_maker}
