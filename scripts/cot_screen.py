"""cot_screen.py — COT conditional diagnostic (cribado, NO una hipótesis).

Condiciona el retorno futuro (1/2/4 semanas) sobre el percentil rodante (3 años) del
neto de especuladores y mide el SHARPE ACTIVO del subconjunto en extremos (p10/90,
p5/95), FADEANDO (specs extremos largos → retorno futuro negativo). No consume
intentos, no toca el holdout, no requiere ficha.

Reporta: Sharpe activo por instrumento y agrupado con IC 95%; n EFECTIVO por EPISODIOS
(no por días, por la autocorrelación 0.85-0.98); bootstrap POR EPISODIO; y el signo.

    uv run python scripts/cot_screen.py
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src import config, cot, engine

INSTR = list(cot.COT_CONTRACTS)
HORIZONS = {"1s": 5, "2s": 10, "4s": 20}     # semanas → días de cotización
ROLL = 156                                    # 3 años de semanas
SEED = 20260823


def _episodes(px: pd.DataFrame, inst: str, lo: float, hi: float, hold_days: int):
    """Devuelve (active_daily_returns, n_episodes, mean_fade_ret, raw_dir) fadeando
    posicionamiento extremo. Un episodio = run contiguo de semanas en extremo (mismo
    lado); se entra en su publicación y se mantiene `hold_days`."""
    w = cot.load_cot(inst)["net_spec"].dropna()
    pct = w.rolling(ROLL, min_periods=52).apply(lambda x: x.rank(pct=True).iloc[-1], raw=False)
    pct = pct.dropna()
    side = pd.Series(0, index=pct.index)
    side[pct >= hi] = -1     # specs muy largos → fade = corto
    side[pct <= lo] = +1     # specs muy cortos → fade = largo
    # episodios: runs contiguos de mismo lado no-cero
    grp = (side != side.shift()).cumsum()
    ret = px[inst]
    ar = engine._asset_returns(px[[inst]])[inst]
    active = []       # series de retornos activos (fade × ret diario) por episodio
    fade_rets = []    # retorno h-días fade por episodio (para signo)
    raw_rets = []     # retorno h-días crudo (para verificar que specs se equivocan)
    n_ep = 0
    for _, idx in side.groupby(grp).groups.items():
        s = side.loc[idx[0]]
        if s == 0:
            continue
        entry = idx[0]                       # fecha de publicación de entrada
        # ventana de holding en el índice de PRECIOS (desde entry, hold_days).
        # COT arranca antes que los precios (FX 2003, índices 2011): sólo episodios
        # con ventana de precio válida cuentan.
        pdates = ret.index[ret.index >= entry][:hold_days]
        p = ret.reindex(pdates).dropna()
        if len(p) < hold_days // 2:
            continue
        n_ep += 1
        active.append(s * ar.reindex(pdates).fillna(0.0))
        fwd = float(p.iloc[-1] / p.iloc[0] - 1)
        fade_rets.append(s * fwd)                     # retorno del fade (>0 si fade gana)
        raw_rets.append(-s * fwd)                     # retorno en la dirección de los specs
    if not active:
        return None
    act = pd.concat(active)
    return act, n_ep, float(np.mean(fade_rets)), float(np.mean(raw_rets))


def _sharpe(act: pd.Series) -> float:
    r = act[act != 0.0]
    sd = r.std(ddof=0)
    return float(np.sqrt(252) * r.mean() / sd) if sd > 0 else 0.0


def _episode_bootstrap(episodes: list[pd.Series], n_boot=1000):
    """IC 95% del Sharpe resampleando EPISODIOS (no días)."""
    rng = np.random.default_rng(SEED)
    n = len(episodes)
    if n < 2:
        return (float("nan"), float("nan"))
    sh = []
    for _ in range(n_boot):
        pick = rng.integers(0, n, n)
        act = pd.concat([episodes[i] for i in pick])
        sh.append(_sharpe(act))
    return (float(np.percentile(sh, 2.5)), float(np.percentile(sh, 97.5)))


def run(lo=0.10, hi=0.90, hold_days=10):
    px = pd.DataFrame({c: pd.read_parquet(config.DATA_CLEAN / f"{c}.parquet")["close"] for c in INSTR})
    rows, pooled_eps = [], []
    for inst in INSTR:
        r = _episodes(px, inst, lo, hi, hold_days)
        if r is None:
            continue
        act, n_ep, fade_mean, raw_dir = r
        # episodios como lista de series para bootstrap
        eps = [g for _, g in act.groupby((act.index.to_series().diff().dt.days > 5).cumsum())]
        pooled_eps += eps
        ci = _episode_bootstrap(eps)
        rows.append({"inst": inst, "n_ep": n_ep, "sharpe": round(_sharpe(act), 2),
                     "ci_lo": round(ci[0], 2), "ci_hi": round(ci[1], 2),
                     "fade_bps": round(fade_mean * 1e4, 1), "signo_ok": raw_dir < 0})
    pooled_act = pd.concat([e for e in pooled_eps])
    pci = _episode_bootstrap(pooled_eps)
    return pd.DataFrame(rows), _sharpe(pooled_act), pci, len(pooled_eps)


def main() -> int:
    for lbl, (lo, hi) in {"p10/90": (0.10, 0.90), "p5/95": (0.05, 0.95)}.items():
        print(f"\n===== umbral {lbl} · holding 2 semanas (fade) =====")
        df, pooled_s, pci, n = run(lo, hi, 10)
        print(df.to_string(index=False))
        print(f"AGRUPADO: Sharpe activo = {pooled_s:+.2f}  IC95[{pci[0]:+.2f}, {pci[1]:+.2f}]  "
              f"(n episodios = {n})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
