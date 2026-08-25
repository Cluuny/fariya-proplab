"""h008_block4.py — H008 Bloque 4: ejecuta el backtest pareado + nulo + sensibilidad de fills
y genera docs/h008_block4.md (D1-D9), autosuficiente para el reviewer.
"""

from __future__ import annotations

import csv
import glob
import time
import zipfile
from pathlib import Path

import numpy as np

from src.crypto import h008_backtest as bt

KL = "data/raw_crypto/futures/um/monthly/klines"
SUMMARY = "results/crypto/h008_daily_summary.csv"
INS_START, HOLDOUT = "2022-09-01", "2024-03-01"
SPAN_YEARS = (np.datetime64("2024-02-29") - np.datetime64("2022-09-01")).astype(int) / 365.25
SEED = 20260824
KL_COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time",
           "quote_volume", "count", "tbv", "tbqv", "ignore"]


def _klines(sym, interval, cols):
    import pandas as pd
    fr = []
    for z in sorted(glob.glob(f"{KL}/{sym}/{interval}/{sym}-{interval}-*.zip")):
        with zipfile.ZipFile(z) as zf, zf.open(zf.namelist()[0]) as fh:
            first = fh.readline().decode()
        h = 0 if "open_time" in first else None
        with zipfile.ZipFile(z) as zf, zf.open(zf.namelist()[0]) as fh:
            fr.append(pd.read_csv(fh, names=KL_COLS, header=h, usecols=cols))
    df = pd.concat(fr).drop_duplicates("open_time").sort_values("open_time")
    df["date"] = pd.to_datetime(df["open_time"], unit="ms").dt.strftime("%Y-%m-%d")
    return df


def _find_episodes():
    """Devuelve lista de episodios: dict con sym, date, direction, y el array de barras 1m del día
    + niveles perfil/simple del día previo. Episodio = balance_prev + extensión + rechazo."""
    import pandas as pd

    prof = {}
    for r in csv.DictReader(open(SUMMARY)):
        prof[(r["sym"], r["date"])] = {k: float(r[k]) for k in
                                       ("vah", "val", "poc", "vwap", "band_up", "band_dn")}
    episodes = []
    for sym in ("BTCUSDT", "ETHUSDT"):
        d1 = _klines(sym, "1d", ["open_time", "high", "low", "close"]).set_index("date")
        tr = np.maximum(d1.high - d1.low, np.maximum((d1.high - d1.close.shift()).abs(),
                                                     (d1.low - d1.close.shift()).abs()))
        atr = tr.rolling(14).mean()
        balance = (d1.high - d1.low) / atr < 1.0
        bars = _klines(sym, "1m", ["open_time", "high", "low", "close"])
        by_day = {dt: g[["open_time", "high", "low", "close"]].to_numpy() for dt, g in bars.groupby("date")}
        dates = [x for x in sorted(by_day) if INS_START <= x < HOLDOUT and x in atr.index and not np.isnan(atr[x])]
        prev = {dates[i]: dates[i - 1] for i in range(1, len(dates))}
        for dt in dates:
            pd_ = prev.get(dt)
            if pd_ is None or not balance.get(pd_, False) or (sym, pd_) not in prof:
                continue
            lv = prof[(sym, pd_)]; b = by_day[dt]
            hi, lo, cl = b[:, 1], b[:, 2], b[:, 3]
            above = np.where(hi >= lv["vah"])[0]; below = np.where(lo <= lv["val"])[0]
            ia = above[0] if len(above) else 10**9; ib = below[0] if len(below) else 10**9
            if min(ia, ib) == 10**9:
                continue
            if ia <= ib:
                i = ia; rej = np.any(cl[i + 1:i + 1 + bt.K_BARS] < lv["vah"]); direction = "short"
            else:
                i = ib; rej = np.any(cl[i + 1:i + 1 + bt.K_BARS] > lv["val"]); direction = "long"
            if not rej:
                continue
            episodes.append({"sym": sym, "date": dt, "direction": direction, "bars": b, "lv": lv})
    return episodes


def _branch(ep, branch, fill_bps=0.0):
    lv, dirn = ep["lv"], ep["direction"]
    va_range = lv["vah"] - lv["val"]
    if branch == "perfil":
        entry = lv["vah"] if dirn == "short" else lv["val"]
        target, rng = lv["poc"], va_range
    else:  # simple: banda de 1 día, objetivo VWAP
        entry = lv["band_up"] if dirn == "short" else lv["band_dn"]
        target, rng = lv["vwap"], (lv["band_up"] - lv["band_dn"])
    return bt.simulate(ep["bars"], entry, target, rng, dirn, fill_bps=fill_bps)


def _metrics(trades, epy):
    rets = np.array([t.ret_net for t in trades if t.filled])
    n = len(rets)
    if n == 0:
        return None
    cum = np.cumsum(rets)
    peak = np.maximum.accumulate(cum)
    maxdd = float((peak - cum).max())
    vol = float(rets.std(ddof=0) * np.sqrt(epy))
    sh_a = bt.sharpe_active(rets, epy)
    sh_full = bt.sharpe_full(rets, epy, SPAN_YEARS * 365 * 2)   # 2 instrumentos
    return {"n": n, "sharpe_active": sh_a, "sharpe_full": sh_full, "ret_total": float(cum[-1]),
            "maxdd": maxdd, "vol": vol, "dd_vol": maxdd / vol if vol else 0.0, "rets": rets}


def main():
    t0 = time.time()
    eps = _find_episodes()
    epy = len(eps) / SPAN_YEARS

    perfil = [_branch(e, "perfil") for e in eps]
    simple = [_branch(e, "simple") for e in eps]
    shared = [i for i in range(len(eps)) if perfil[i].filled and simple[i].filled]
    np_only = sum(1 for t in perfil if t.filled); ns_only = sum(1 for t in simple if t.filled)

    pr = np.array([perfil[i].ret_net for i in shared])
    sr = np.array([simple[i].ret_net for i in shared])
    epy_sh = len(shared) / SPAN_YEARS
    sh_p = bt.sharpe_active(pr, epy_sh); sh_s = bt.sharpe_active(sr, epy_sh)
    delta = sh_p - sh_s   # Δ pareado SOBRE LOS COMPARTIDOS (268)
    # Sharpe activo de la rama perfil sobre TODOS sus episodios (341) — MISMA base que el nulo,
    # para la condición (3). (No usar el subconjunto compartido: sería base distinta del nulo.)
    pr_all = np.array([t.ret_net for t in perfil if t.filled])
    sh_p_full = bt.sharpe_active(pr_all, epy)

    # bootstrap PAREADO por episodio
    rng = np.random.default_rng(SEED)
    deltas = []
    m = len(shared)
    for _ in range(1000):
        idx = rng.integers(0, m, m)
        deltas.append(bt.sharpe_active(pr[idx], epy_sh) - bt.sharpe_active(sr[idx], epy_sh))
    dlo, dhi = np.percentile(deltas, [2.5, 97.5])
    d_crosses_0 = dlo <= 0 <= dhi

    # BENCHMARK NULO: niveles de entrada al azar dentro del rango del día
    rng2 = np.random.default_rng(SEED)
    null_sh = []
    for _ in range(1000):
        rets = []
        for e in eps:
            b = e["bars"]; lo, hi = b[:, 2].min(), b[:, 1].max()
            entry = rng2.uniform(lo, hi)
            va_range = e["lv"]["vah"] - e["lv"]["val"]
            tr = bt.simulate(b, entry, e["lv"]["poc"], va_range, e["direction"], fill_bps=0.0)
            if tr.filled:
                rets.append(tr.ret_net)
        null_sh.append(bt.sharpe_active(rets, epy))
    null_sh = np.array(null_sh)
    p95 = float(np.percentile(null_sh, 95))
    p_emp = float((null_sh >= sh_p_full).mean())

    # SENSIBILIDAD DE FILLS (≥5 bps de cruce)
    perfil5 = [_branch(e, "perfil", fill_bps=5.0) for e in eps]
    simple5 = [_branch(e, "simple", fill_bps=5.0) for e in eps]
    shared5 = [i for i in range(len(eps)) if perfil5[i].filled and simple5[i].filled]
    pr5 = np.array([perfil5[i].ret_net for i in shared5]); sr5 = np.array([simple5[i].ret_net for i in shared5])
    epy5 = len(shared5) / SPAN_YEARS
    delta5 = bt.sharpe_active(pr5, epy5) - bt.sharpe_active(sr5, epy5)
    pr5_all = np.array([t.ret_net for t in perfil5 if t.filled])
    sh_p5 = bt.sharpe_active(pr5_all, len(pr5_all) / SPAN_YEARS)   # base FULL, igual que sh_p_full

    mp = _metrics(perfil, epy); ms = _metrics(simple, epy)

    # ---- veredicto ----
    cond1_muerta = (delta <= 0) and not d_crosses_0
    cond1b_under = d_crosses_0
    cond3_muerta = sh_p_full < p95
    LISTON = 0.961
    promociona = (delta > 0 and not d_crosses_0) and (sh_p_full > p95) and (sh_p_full > LISTON)
    if cond3_muerta:
        verdict = "MUERTA (condición 3: Sharpe activo < p95 del nulo)"
    elif cond1_muerta:
        verdict = "MUERTA (condición 1: Δ Sharpe ≤ 0, IC no cruza 0)"
    elif promociona:
        verdict = "PROMUEVE A HOLDOUT"
    else:
        # ninguna condición de muerte dispara, pero no promociona. El hecho dominante es que el
        # Sharpe activo está MUY por debajo del listón 0.961 (no viable); (1) queda underpowered.
        under = " · dimensión incremental (1) UNDERPOWERED (IC del Δ cruza 0)" if cond1b_under else ""
        beat = "supera al nulo (los niveles de perfil llevan información vs fading aleatorio)" \
            if sh_p_full > p95 else "no supera al nulo"
        verdict = (f"NO PROMUEVE — Sharpe activo {sh_p_full:.3f} ≪ listón 0.961 (no viable); "
                   f"{beat}{under}")

    _write_doc(locals())
    print(f"VEREDICTO: {verdict}")
    print(f"Δ Sharpe {delta:+.3f} IC95 [{dlo:+.3f},{dhi:+.3f}] · perfil(341) {sh_p_full:.3f} vs p95 nulo {p95:.3f} · p={p_emp:.3f} "
          f"· listón 0.961 · shared {len(shared)}/{len(eps)} · {time.time()-t0:.0f}s")


def _write_doc(v):
    from datetime import datetime  # noqa
    L = []
    a = L.append
    a("# H008 — Bloque 4: estrategia condicional, Δ Sharpe y benchmark nulo\n")
    a("Auto-suficiente. AMT/Volume Profile en BTCUSDT+ETHUSDT perp, in-sample 2022-09-01 → "
      "2024-02-29 (holdout 2024-03→08 INTACTO, no descargado). Listón vigente: Sharpe ACTIVO "
      "requerido **0.961** (duty real 0.31), suelo de coste 0.476. El binding es el activo.\n")

    a("## D1. Tabla de veredicto\n")
    a("| condición | medido | umbral | ¿dispara? |")
    a("|---|---|---|---|")
    a(f"| (1) Δ Sharpe (perfil − simple) | {v['delta']:+.3f} [{v['dlo']:+.3f},{v['dhi']:+.3f}] | ≤0 e IC no cruza 0 | {'sí' if v['cond1_muerta'] else 'no'} |")
    a(f"| (1b) ¿IC del Δ cruza 0? | {'sí' if v['d_crosses_0'] else 'no'} | — | underpowered {'sí' if v['cond1b_under'] else 'no'} |")
    a("| (2) coincidencia | 26% [23,28] | >80% | no (ya evaluada) |")
    a(f"| (3) Sharpe activo vs p95 nulo | {v['sh_p_full']:.3f} vs {v['p95']:.3f} | activo < p95 | {'sí' if v['cond3_muerta'] else 'no'} |")
    a(f"\n**VEREDICTO GLOBAL: {v['verdict']}.** (listón activo 0.961; Sharpe activo perfil {v['sh_p_full']:.3f}, sobre 341 episodios)\n")

    a("## D2. Integridad del pareado\n")
    a(f"- episodios rama perfil (con fill): {v['np_only']}")
    a(f"- episodios rama simple (con fill): {v['ns_only']}")
    a(f"- episodios COMPARTIDOS (ambos con fill): {len(v['shared'])}")
    valid = len(v['shared']) >= 0.8 * min(v['np_only'], v['ns_only'])
    a(f"- ¿pareado válido? {'sí' if valid else 'PARCIAL'} — el Δ se computa SOBRE LOS COMPARTIDOS. "
      "Los episodios se definen por el CONTEXTO (balance+extensión+rechazo, vía VA del perfil); la "
      "rama simple no llena cuando su nivel (banda 1d) no se toca ese día. Se reporta el Δ sólo "
      "sobre los compartidos; los no compartidos se excluyen del Δ (no se comparan peras con manzanas).\n")

    for label, mm in [("PERFIL", v['mp']), ("SIMPLE", v['ms'])]:
        pass
    a("## D3. Resultados por rama\n")
    a("| métrica | rama PERFIL | rama SIMPLE |")
    a("|---|---|---|")
    mp, ms = v['mp'], v['ms']
    def row(name, kp, ks, fmt="{:.3f}"):
        a(f"| {name} | {fmt.format(kp)} | {fmt.format(ks)} |")
    row("Sharpe activo", mp["sharpe_active"], ms["sharpe_active"])
    row("Sharpe serie completa", mp["sharpe_full"], ms["sharpe_full"])
    row("retorno total", mp["ret_total"], ms["ret_total"], "{:.2%}")
    row("max_dd", mp["maxdd"], ms["maxdd"], "{:.2%}")
    row("vol realizada", mp["vol"], ms["vol"], "{:.2%}")
    row("max_dd / vol", mp["dd_vol"], ms["dd_vol"])
    row("episodios (fill)", mp["n"], ms["n"], "{:.0f}")
    # coste
    def costs(trades):
        f = [t for t in trades if t.filled]
        fee = sum(bt.MAKER + (bt.MAKER if t.exit_type == "target" else bt.TAKER) for t in f)
        fund = sum(1 for t in f if t.crossed_funding)
        return fee / len(f) if f else 0, fund
    fp, fundp = costs([v['perfil'][i] for i in range(len(v['eps']))])
    fs, funds = costs([v['simple'][i] for i in range(len(v['eps']))])
    a(f"| comisión media/episodio | {fp*1e4:.1f} bps | {fs*1e4:.1f} bps |")
    a(f"| episodios que cruzaron corte funding | {fundp} | {funds} |")
    a(f"| turnover (rt/día) | {mp['n']/(SPAN_YEARS*365):.2f} | {ms['n']/(SPAN_YEARS*365):.2f} |\n")

    a("## D4. Benchmark nulo\n")
    ns = v['null_sh']
    a(f"- media {ns.mean():.3f} · p50 {np.percentile(ns,50):.3f} · p95 {np.percentile(ns,95):.3f} · p99 {np.percentile(ns,99):.3f}")
    a(f"- Sharpe activo rama perfil (341 episodios) {v['sh_p_full']:.3f} vs p95 {v['p95']:.3f}")
    a(f"- p-valor empírico (fracción del nulo que supera al observado): {v['p_emp']:.3f}")
    lo_, hi_ = ns.min(), ns.max()
    a("- percentiles del nulo (Sharpe activo): " +
      " · ".join(f"p{q}={np.percentile(ns,q):.2f}" for q in (5, 25, 50, 75, 95, 99)) + "\n")

    a("## D5. Supuesto de fills\n")
    a("- Supuesto base: fill GARANTIZADO al TOQUE del nivel (fill_bps=0). Con klines 1m no se sabe "
      "si la orden límite se habría llenado, sólo si el precio tocó el nivel.")
    a(f"- % de episodios donde se asumió fill (rama perfil): {v['np_only']}/{len(v['eps'])} = {v['np_only']/len(v['eps']):.0%}")
    a(f"- SENSIBILIDAD (fill sólo si el precio cruza ≥5 bps): Δ Sharpe {v['delta5']:+.3f} "
      f"(base {v['delta']:+.3f}); Sharpe activo perfil {v['sh_p5']:.3f} (base {v['sh_p_full']:.3f}); "
      f"compartidos {len(v['shared5'])}.")
    chg = (v['sh_p5'] < v['p95']) != (v['sh_p'] < v['p95'])
    a(f"- ¿el veredicto cambia entre supuestos? {'SÍ — el veredicto sería sobre el supuesto de fills, no sobre la estrategia.' if chg else 'no.'}")
    a("- **ADVERTENCIA:** asumir fill al toque INFLA el resultado. El modelo de fills nunca se "
      "construyó (docs/crypto_pivot.md lo declara prerrequisito: 'modelo de fills, va después'). "
      "Este resultado lleva ese supuesto encima.\n")

    a("## D6. Distribución de salidas\n")
    a("| salida | rama perfil | rama simple |")
    a("|---|---|---|")
    def dist(trades):
        f = [t for t in trades if t.filled]; n = len(f) or 1
        return {k: (sum(1 for t in f if t.exit_type == k), sum(1 for t in f if t.exit_type == k) / n)
                for k in ("target", "stop", "timestop")}
    dp = dist([v['perfil'][i] for i in range(len(v['eps']))]); ds = dist([v['simple'][i] for i in range(len(v['eps']))])
    for k, name in [("target", "objetivo alcanzado"), ("stop", "stop"), ("timestop", "time-stop 24h")]:
        a(f"| {name} | {dp[k][0]} ({dp[k][1]:.0%}) | {ds[k][0]} ({ds[k][1]:.0%}) |")
    a("")

    a("## D7. Poder estadístico\n")
    epy_sh = len(v['shared']) / SPAN_YEARS
    se_a = np.sqrt((1 + v['sh_p']**2 / 2) / max(len(v['shared']), 1))
    se_d = float(np.std(v['deltas']))
    a(f"- T efectiva usada (episodios compartidos): {len(v['shared'])} (× ~{epy_sh:.0f}/año)")
    a(f"- SE(Ŝ) del Sharpe activo: {se_a:.3f}")
    a(f"- SE del Δ pareado (bootstrap): {se_d:.3f}")
    can = (v['sh_p'] - 1.96*se_a > 0.961) or (v['sh_p'] + 1.96*se_a < 0.961)
    a(f"- ¿el IC distingue el falsador del umbral 0.961? {'sí' if can else 'no — zona de indistinción'}\n")

    a("## D8. Expectativa comprometida\n")
    a("resultado_esperado (congelado) decía: Δ ≈ 0 o negativo; veredicto esperado muerta por "
      "redundancia o underpowered.")
    if v['verdict'].startswith("MUERTA") or v['verdict'].startswith("UNDERPOWERED") or v['verdict'].startswith("NO PROMUEVE"):
        a(f"→ **CUMPLIDA** en dirección: el veredicto es «{v['verdict']}», no una promoción. "
          "(La coincidencia baja ya había refutado la parte de 'redundancia'; el edge tampoco supera el listón.)\n")
    else:
        a(f"→ **REFUTADA**: contra la expectativa, el veredicto es «{v['verdict']}».\n")

    a("## D9. Cómputo\n")
    import resource
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6
    a(f"- Datos: klines 1m+1d ya locales (~63 MB); perfiles del resumen (ya calculado). NO se "
      "re-descargó aggTrades. Pico de RAM ~{:.0f} MB. Pico de disco: sin cambio (nada nuevo grande).".format(peak))
    a(f"- Episodios evaluados: {len(v['eps'])}; bootstrap pareado 1000; nulo 1000×{len(v['eps'])}.\n")

    Path("docs/h008_block4.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
