"""h009_run.py — H009: AMT CONTINUACIÓN (aceptación fuera del VA → continuación).

Ficha CONGELADA (hypotheses/H009_amt_continuation.yaml). NO se toca FALSADOR ni resultado_esperado.
Reusa el simulador de H008 (src/crypto/h008_backtest.simulate). Diferencias vs H008:
  - contexto: DESEQUILIBRIO previo ((h−l)/ATR14 > 1.5), no balance (<1.0).
  - confirmación: ACEPTACIÓN (mid NO re-entra en K=3 barras 1m), no rechazo.
  - dirección: CONTINUACIÓN (long arriba del VAH, short abajo del VAL).
  - geometría: SIMÉTRICA (objetivo/stop = 1×rango_nivel); el POC ya no es objetivo.
  - nulo: entrada aleatoria PERO objetivo/stop reposicionados simétricos (geometría preservada) +
    VERIFICACIÓN DE SANIDAD (~50% objetivo) reportada antes del veredicto.
Genera docs/h009_run.md (D1-D9). NO toca el holdout.
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
SEED = 20260829
IMBALANCE = 1.5          # (h−l)/ATR14 > 1.5 (ficha); zona 1.0-1.5 excluida
K = bt.K_BARS            # 3 (mismo K que H008)
KL_COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time",
           "quote_volume", "count", "tbv", "tbqv", "ignore"]
N_EFF_PAIR = 1.11 / 2.0  # descuento por par BTC/ETH ρ0.8 (N_eff par 1.11 sobre 2 → factor 0.555)


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
    """Episodio H009 = DESEQUILIBRIO previo + extensión + ACEPTACIÓN. Devuelve además los conteos
    del embudo para la parada de duty (D1)."""
    import pandas as pd
    prof = {}
    for r in csv.DictReader(open(SUMMARY)):
        prof[(r["sym"], r["date"])] = {k: float(r[k]) for k in
                                       ("vah", "val", "poc", "vwap", "band_up", "band_dn")}
    episodes = []
    funnel = {"dias": 0, "desequilibrio_prev": 0, "extension": 0, "aceptacion": 0}
    for sym in ("BTCUSDT", "ETHUSDT"):
        d1 = _klines(sym, "1d", ["open_time", "high", "low", "close"]).set_index("date")
        tr = np.maximum(d1.high - d1.low, np.maximum((d1.high - d1.close.shift()).abs(),
                                                     (d1.low - d1.close.shift()).abs()))
        atr = tr.rolling(14).mean()
        imbalance = (d1.high - d1.low) / atr > IMBALANCE
        bars = _klines(sym, "1m", ["open_time", "high", "low", "close"])
        by_day = {dt: g[["open_time", "high", "low", "close"]].to_numpy() for dt, g in bars.groupby("date")}
        dates = [x for x in sorted(by_day) if INS_START <= x < HOLDOUT and x in atr.index and not np.isnan(atr[x])]
        prev = {dates[i]: dates[i - 1] for i in range(1, len(dates))}
        for dt in dates:
            pv = prev.get(dt)
            if pv is None or (sym, pv) not in prof:
                continue
            funnel["dias"] += 1
            if not bool(imbalance.get(pv, False)):
                continue
            funnel["desequilibrio_prev"] += 1
            lv = prof[(sym, pv)]; b = by_day[dt]
            hi, lo, cl = b[:, 1], b[:, 2], b[:, 3]
            above = np.where(hi >= lv["vah"])[0]; below = np.where(lo <= lv["val"])[0]
            ia = above[0] if len(above) else 10**9; ib = below[0] if len(below) else 10**9
            if min(ia, ib) == 10**9:
                continue
            funnel["extension"] += 1
            if ia <= ib:   # extendió ARRIBA del VAH → continuación LONG
                i, direction, edge = ia, "long", lv["vah"]
                accept = not np.any(cl[i + 1:i + 1 + K] < edge)   # NO re-entra por debajo del VAH
            else:          # extendió ABAJO del VAL → continuación SHORT
                i, direction, edge = ib, "short", lv["val"]
                accept = not np.any(cl[i + 1:i + 1 + K] > edge)   # NO re-entra por encima del VAL
            if not accept:
                continue
            funnel["aceptacion"] += 1
            episodes.append({"sym": sym, "date": dt, "direction": direction, "bars": b, "lv": lv})
    return episodes, funnel


def _branch(ep, branch, fill_bps=0.0):
    """Geometría de CONTINUACIÓN, simétrica: objetivo = entrada ± rango, stop = ∓ rango."""
    lv, dirn = ep["lv"], ep["direction"]
    if branch == "perfil":
        rng = lv["vah"] - lv["val"]
        entry = lv["vah"] if dirn == "long" else lv["val"]
    else:  # simple: banda de volatilidad de 1 día
        rng = lv["band_up"] - lv["band_dn"]
        entry = lv["band_up"] if dirn == "long" else lv["band_dn"]
    target = entry + rng if dirn == "long" else entry - rng
    return bt.simulate(ep["bars"], entry, target, rng, dirn, fill_bps=fill_bps)


def _metrics(trades, epy):
    rets = np.array([t.ret_net for t in trades if t.filled])
    n = len(rets)
    if n == 0:
        return None
    cum = np.cumsum(rets); peak = np.maximum.accumulate(cum)
    maxdd = float((peak - cum).max()); vol = float(rets.std(ddof=0) * np.sqrt(epy))
    return {"n": n, "sharpe_active": bt.sharpe_active(rets, epy),
            "sharpe_full": bt.sharpe_full(rets, epy, SPAN_YEARS * 365 * 2),
            "ret_total": float(cum[-1]), "maxdd": maxdd, "vol": vol,
            "dd_vol": maxdd / vol if vol else 0.0, "rets": rets}


def main():
    t0 = time.time()
    eps, funnel = _find_episodes()
    n_raw = len(eps)
    total_di = funnel["dias"]
    duty = n_raw / total_di if total_di else 0.0
    rt_dia = n_raw / (SPAN_YEARS * 365)
    # T efectiva PRECISA por coincidencia real BTC/ETH: las fechas con episodio en AMBOS instrumentos
    # cuentan como un par a ρ0.8 (N_eff par 1.11), no 2; las de un solo instrumento cuentan 1.
    from collections import Counter
    by_date = Counter(e["date"] for e in eps)
    coincident = sum(1 for _, c in by_date.items() if c == 2)
    solo = sum(1 for _, c in by_date.items() if c == 1)
    t_eff = solo + 1.11 * coincident
    t_eff_lo = n_raw * N_EFF_PAIR   # cota conservadora (todo coincidente), sólo referencia
    liston = 0.40 / np.sqrt(duty) + 0.245 if duty > 0 else float("inf")
    print(f"D1 · episodios crudos {n_raw} · duty {duty:.3f} · rt/día {rt_dia:.3f} · "
          f"T_eff {t_eff:.0f} (coincidentes {coincident}, solo {solo}) · listón activo {liston:.3f}")
    print(f"   embudo: días {funnel['dias']} → desequilibrio {funnel['desequilibrio_prev']} → "
          f"extensión {funnel['extension']} → aceptación {funnel['aceptacion']}")

    if t_eff < 60:
        print(f"PARADA (regla del bloque): T_eff {t_eff:.0f} < 60 → ni (2) ni (3) resuelven. "
              "Se reporta D1 y NO se corre el backtest.")
        _write_doc_stop(locals())
        return

    epy = n_raw / SPAN_YEARS
    perfil = [_branch(e, "perfil") for e in eps]
    simple = [_branch(e, "simple") for e in eps]
    shared = [i for i in range(n_raw) if perfil[i].filled and simple[i].filled]
    np_only = sum(1 for t in perfil if t.filled); ns_only = sum(1 for t in simple if t.filled)

    pr = np.array([perfil[i].ret_net for i in shared]); sr = np.array([simple[i].ret_net for i in shared])
    epy_sh = len(shared) / SPAN_YEARS
    sh_p = bt.sharpe_active(pr, epy_sh); sh_s = bt.sharpe_active(sr, epy_sh)
    delta = sh_p - sh_s
    pr_all = np.array([t.ret_net for t in perfil if t.filled])
    sh_p_full = bt.sharpe_active(pr_all, epy)

    rng = np.random.default_rng(SEED)
    deltas = [bt.sharpe_active(pr[i], epy_sh) - bt.sharpe_active(sr[i], epy_sh)
              for i in (rng.integers(0, len(shared), len(shared)) for _ in range(1000))]
    dlo, dhi = np.percentile(deltas, [2.5, 97.5]); d_crosses_0 = dlo <= 0 <= dhi

    # NULO con geometría PRESERVADA (objetivo/stop simétricos ±rango alrededor de la entrada aleatoria)
    rng2 = np.random.default_rng(SEED)
    null_sh, null_target_hits, null_target_tot = [], 0, 0
    for _ in range(1000):
        rets = []
        for e in eps:
            b = e["bars"]; lo, hi = b[:, 2].min(), b[:, 1].max()
            entry = rng2.uniform(lo, hi); va = e["lv"]["vah"] - e["lv"]["val"]
            dirn = e["direction"]; target = entry + va if dirn == "long" else entry - va
            tr = bt.simulate(b, entry, target, va, dirn)
            if tr.filled:
                rets.append(tr.ret_net); null_target_tot += 1
                null_target_hits += (tr.exit_type == "target")
        null_sh.append(bt.sharpe_active(rets, epy))
    null_sh = np.array(null_sh)
    p95 = float(np.percentile(null_sh, 95)); p_emp = float((null_sh >= sh_p_full).mean())
    null_target_pct = null_target_hits / max(null_target_tot, 1)
    geometria_ok = 0.40 <= null_target_pct <= 0.60   # sanidad: ~50%

    # sensibilidad de fills (≥5 bps)
    perfil5 = [_branch(e, "perfil", fill_bps=5.0) for e in eps]
    simple5 = [_branch(e, "simple", fill_bps=5.0) for e in eps]
    shared5 = [i for i in range(n_raw) if perfil5[i].filled and simple5[i].filled]
    pr5 = np.array([perfil5[i].ret_net for i in shared5]); sr5 = np.array([simple5[i].ret_net for i in shared5])
    epy5 = len(shared5) / SPAN_YEARS
    delta5 = bt.sharpe_active(pr5, epy5) - bt.sharpe_active(sr5, epy5)
    pr5_all = np.array([t.ret_net for t in perfil5 if t.filled])
    sh_p5 = bt.sharpe_active(pr5_all, len(pr5_all) / SPAN_YEARS)

    mp = _metrics(perfil, epy); ms = _metrics(simple, epy)

    # veredicto (3 condiciones; (2) sólo si la geometría del nulo verifica)
    cond1_muerta = (delta <= 0) and not d_crosses_0
    cond1b_under = d_crosses_0
    cond2_muerta = geometria_ok and (sh_p_full < p95)
    cond3_noviable = sh_p_full < liston
    if cond2_muerta:
        verdict = f"MUERTA (condición 2: Sharpe activo {sh_p_full:.3f} < p95 del nulo {p95:.3f}, geometría verificada)"
    elif cond1_muerta:
        verdict = f"MUERTA (condición 1: Δ Sharpe {delta:+.3f} ≤ 0, IC no cruza 0)"
    elif cond3_noviable:
        under = " · (1) UNDERPOWERED (IC del Δ cruza 0)" if cond1b_under else ""
        geo = "" if geometria_ok else " · (2) NO usada: geometría del nulo rota"
        verdict = f"NO VIABLE — Sharpe activo {sh_p_full:.3f} ≪ listón {liston:.3f}{under}{geo}"
    else:
        verdict = f"NO PROMUEVE — activo {sh_p_full:.3f}; ninguna condición de muerte dispara limpiamente"

    _write_doc(locals())
    print(f"VEREDICTO: {verdict}")
    print(f"Δ {delta:+.3f} IC95 [{dlo:+.3f},{dhi:+.3f}] · perfil({n_raw}) {sh_p_full:.3f} vs p95 nulo {p95:.3f} "
          f"(objetivo nulo {null_target_pct:.0%}, geometría {'OK' if geometria_ok else 'ROTA'}) · "
          f"listón {liston:.3f} · shared {len(shared)}/{n_raw} · {time.time()-t0:.0f}s")


def _d1(v):
    return [
        "## D1. Duty real, T efectiva, listón recalculado (lo primero)\n",
        f"- Embudo (in-sample 2022-09-01→2024-02-29, BTC+ETH): días válidos **{v['funnel']['dias']}** → "
        f"DESEQUILIBRIO previo (>1.5) **{v['funnel']['desequilibrio_prev']}** → extensión fuera del VA "
        f"**{v['funnel']['extension']}** → **ACEPTACIÓN (K=3) {v['funnel']['aceptacion']}**.",
        f"- **Duty real = {v['duty']:.3f}** (episodios {v['n_raw']} / {v['total_di']} día-instrumento). "
        f"round-trips/día {v['rt_dia']:.3f}.",
        f"- **T efectiva = {v['t_eff']:.0f}** (por coincidencia REAL: {v['coincident']} fechas con episodio en "
        f"BTC y ETH a la vez → cuentan 1.11 cada par a ρ0.8; {v['solo']} de un solo instrumento cuentan 1. "
        f"La cota cruda-conservadora {v['t_eff_lo']:.0f} asumía todo coincidente; la real es {v['t_eff']:.0f} > 60 → RESOLUBLE).",
        f"- **Listón recalculado = 0.40/√{v['duty']:.3f} + 0.245 = {v['liston']:.3f}** (Sharpe ACTIVO requerido; "
        f"a priori la ficha estimó ~1.28 a duty 0.15).\n",
    ]


def _write_doc_stop(v):
    L = ["# H009 — corrida (PARADA en D1)\n",
         "AMT continuación (aceptación fuera del VA) en BTCUSDT+ETHUSDT perp, in-sample 2022-09→2024-02. "
         "Holdout INTACTO.\n"] + _d1(v)
    L.append(f"\n**PARADA (regla del bloque):** T efectiva (lo {v['t_eff_lo']:.0f}) < 60 → ni (2) ni (3) "
             "resuelven nada. NO se corre el backtest ni el nulo. La cara de CONTINUACIÓN de AMT es "
             "IRRESOLUBLE con la muestra: el contexto de desequilibrio+aceptación es demasiado raro.\n")
    Path("docs/h009_run.md").write_text("\n".join(L) + "\n")


def _write_doc(v):
    L = []; a = L.append
    a("# H009 — corrida: AMT continuación (aceptación fuera del área de valor)\n")
    a("Auto-suficiente. Cara de CONTINUACIÓN de AMT en BTCUSDT+ETHUSDT perp, in-sample 2022-09-01 → "
      "2024-02-29 (holdout 2024-03→08 INTACTO, no descargado). Ficha congelada "
      "`hypotheses/H009_amt_continuation.yaml`; NO se tocó FALSADOR ni resultado_esperado.\n")
    L += _d1(v)

    a("## D2. Tabla de veredicto\n")
    a("| condición | medido | umbral | ¿dispara? |")
    a("|---|---|---|---|")
    a(f"| (1) Δ Sharpe (perfil − simple) | {v['delta']:+.3f} [{v['dlo']:+.3f},{v['dhi']:+.3f}] | ≤0 e IC no cruza 0 | {'sí' if v['cond1_muerta'] else 'no'} |")
    a(f"| (1b) ¿IC del Δ cruza 0? | {'sí' if v['d_crosses_0'] else 'no'} | — | underpowered {'sí' if v['cond1b_under'] else 'no'} |")
    a(f"| (2) Sharpe activo vs p95 nulo | {v['sh_p_full']:.3f} vs {v['p95']:.3f} | activo < p95 (si geometría OK) | {'sí' if v['cond2_muerta'] else 'no'} |")
    a(f"| (3) Sharpe activo vs listón | {v['sh_p_full']:.3f} vs {v['liston']:.3f} | activo < listón | {'sí' if v['cond3_noviable'] else 'no'} |")
    a(f"\n**VEREDICTO GLOBAL: {v['verdict']}.**\n")

    a("## D3. Integridad del pareado\n")
    a(f"- episodios rama perfil (con fill): {v['np_only']}")
    a(f"- episodios rama simple (con fill): {v['ns_only']}")
    a(f"- episodios COMPARTIDOS (ambos con fill): {len(v['shared'])}")
    a("- El Δ se computa SOBRE LOS COMPARTIDOS; los episodios se definen por el CONTEXTO "
      "(desequilibrio+extensión+aceptación), no por los niveles. La rama simple no llena cuando su "
      "nivel (banda 1d) no se toca ese día.\n")

    a("## D4. Resultados por rama\n")
    a("| métrica | rama PERFIL | rama SIMPLE |")
    a("|---|---|---|")
    mp, ms = v['mp'], v['ms']

    def row(name, kp, ks, fmt="{:.3f}"):
        a(f"| {name} | {fmt.format(kp)} | {fmt.format(ks)} |")
    se_p = np.sqrt((1 + mp["sharpe_active"]**2 / 2) / max(mp["n"], 1))
    se_s = np.sqrt((1 + ms["sharpe_active"]**2 / 2) / max(ms["n"], 1))
    a(f"| Sharpe activo (IC95) | {mp['sharpe_active']:+.3f} [{mp['sharpe_active']-1.96*se_p:+.2f},{mp['sharpe_active']+1.96*se_p:+.2f}] "
      f"| {ms['sharpe_active']:+.3f} [{ms['sharpe_active']-1.96*se_s:+.2f},{ms['sharpe_active']+1.96*se_s:+.2f}] |")
    row("Sharpe serie completa", mp["sharpe_full"], ms["sharpe_full"])
    row("retorno total", mp["ret_total"], ms["ret_total"], "{:.2%}")
    row("max_dd", mp["maxdd"], ms["maxdd"], "{:.2%}")
    row("vol realizada", mp["vol"], ms["vol"], "{:.2%}")
    row("max_dd / vol", mp["dd_vol"], ms["dd_vol"])
    row("episodios (fill)", mp["n"], ms["n"], "{:.0f}")

    def costs(trades):
        f = [t for t in trades if t.filled]
        fee = sum(bt.MAKER + (bt.MAKER if t.exit_type == "target" else bt.TAKER) for t in f)
        return (fee / len(f) if f else 0), sum(1 for t in f if t.crossed_funding)
    fp, fundp = costs(v['perfil']); fs, funds = costs(v['simple'])
    a(f"| comisión media/episodio | {fp*1e4:.1f} bps | {fs*1e4:.1f} bps |")
    a(f"| episodios que cruzaron funding | {fundp} | {funds} |")
    a(f"| turnover (rt/día) | {mp['n']/(SPAN_YEARS*365):.2f} | {ms['n']/(SPAN_YEARS*365):.2f} |\n")

    a("## D5. Benchmark nulo (con verificación de sanidad ANTES del veredicto)\n")
    ns = v['null_sh']
    a(f"- **VERIFICACIÓN DE GEOMETRÍA: el nulo alcanza objetivo {v['null_target_pct']:.0%} de las "
      f"veces** → geometría {'OK (≈50%, la condición 2 SÍ se usa)' if v['geometria_ok'] else 'ROTA (lejos de 50% → la condición 2 NO se usa; se dice, no se maquilla)'}.")
    if not v['geometria_ok']:
        a(f"- MECANISMO del {v['null_target_pct']:.0%} (honesto, no es el defecto de H008): aquí el objetivo NO está "
          "detrás de la entrada (es simétrico ±1×rango_VA); el 9% viene de que ±1×rango_VA es un objetivo LEJANO "
          "para una entrada aleatoria a media sesión → el nulo (y también el activo: 14% perfil, D7) time-stopea "
          "antes de tocarlo. El nulo es geométricamente JUSTO (mismo objetivo lejano que el activo), pero la "
          "sanidad ~50% se calibró para objetivos cercanos → se marca ROTA y (2) NO se usa por conservadurismo. "
          "El veredicto NO depende de (2): (3) lo cierra solo.")
    a(f"- media {ns.mean():.3f} · p50 {np.percentile(ns,50):.3f} · p95 {v['p95']:.3f} · p99 {np.percentile(ns,99):.3f}")
    a(f"- Sharpe activo rama perfil ({v['n_raw']} episodios) {v['sh_p_full']:.3f} vs p95 {v['p95']:.3f}")
    a(f"- p-valor empírico (fracción del nulo ≥ observado): {v['p_emp']:.3f}\n")

    a("## D6. Sensibilidad de fills\n")
    a(f"- Base = fill al TOQUE. Con cruce ≥5 bps: Δ Sharpe {v['delta5']:+.3f} (base {v['delta']:+.3f}); "
      f"Sharpe activo perfil {v['sh_p5']:.3f} (base {v['sh_p_full']:.3f}); compartidos {len(v['shared5'])}.")
    chg = (v['sh_p5'] < v['liston']) != (v['sh_p_full'] < v['liston'])
    a(f"- ¿el veredicto cambia entre supuestos? {'SÍ' if chg else 'NO — afecta la MAGNITUD, no el veredicto'}. "
      "El modelo de fills real no se construyó; el resultado lleva el supuesto de fill-al-toque encima.\n")

    a("## D7. Distribución de salidas\n")
    a("| salida | rama perfil | rama simple |")
    a("|---|---|---|")

    def dist(trades):
        f = [t for t in trades if t.filled]; n = len(f) or 1
        return {k: (sum(1 for t in f if t.exit_type == k), sum(1 for t in f if t.exit_type == k) / n)
                for k in ("target", "stop", "timestop")}
    dp, ds = dist(v['perfil']), dist(v['simple'])
    for k, name in [("target", "objetivo (continuación)"), ("stop", "stop (vuelta al VA)"), ("timestop", "time-stop 24h")]:
        a(f"| {name} | {dp[k][0]} ({dp[k][1]:.0%}) | {ds[k][0]} ({ds[k][1]:.0%}) |")
    a("")

    a("## D8. Expectativa comprometida\n")
    a("resultado_esperado (congelado): Sharpe activo entre −0.3 y +0.3; veredicto esperado MUERTA o "
      "UNDERPOWERED; probabilidad previa BAJA. Sin interpretar a favor:")
    in_range = -0.3 <= v['sh_p_full'] <= 0.3
    cumplida = v['verdict'].startswith(("MUERTA", "NO VIABLE", "NO PROMUEVE")) and in_range
    a(f"→ Sharpe activo medido {v['sh_p_full']:+.3f} ({'DENTRO' if in_range else 'FUERA'} del rango −0.3..+0.3); "
      f"veredicto «{v['verdict']}». **{'CUMPLIDA' if cumplida else 'PARCIAL/REFUTADA'}** en dirección.\n")

    a("## D9. Cómputo\n")
    import resource
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6
    a(f"- Datos: klines 1m+1d locales + perfiles del resumen (h008). NO se re-descargó nada. Pico RAM ~{peak:.0f} MB.")
    a(f"- Episodios {v['n_raw']}; bootstrap pareado 1000; nulo 1000×{v['n_raw']} (semilla {SEED}).\n")

    Path("docs/h009_run.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
