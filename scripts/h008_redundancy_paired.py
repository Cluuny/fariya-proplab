"""h008_redundancy_paired.py — H008: coincidencia BIEN EMPAREJADA (interior vs interior).

Corrige el emparejamiento del diagnóstico original (VAH interior vs máximo extremo, coincidencia
garantizada baja por geometría). Ahora INTERIOR contra INTERIOR, aritmética pura sobre datos ya
descargados (aggTrades + klines 1d), sin estrategia ni benchmark:

  |VAH − Bollinger_sup(20, 2σ)| / precio ≤ 10 bps
  |VAL − Bollinger_inf(20, 2σ)| / precio ≤ 10 bps
  |POC − SMA(20)|              / precio ≤ 10 bps
  |POC − VWAP(24h)|            / precio ≤ 10 bps   (ATENCIÓN: ambos son precio ponderado por
                                                    volumen sobre la misma ventana → si coinciden
                                                    mucho, el POC es un VWAP caro)

Reporta cada uno con % e IC95, un agregado "cualquiera", y la DISTRIBUCIÓN de las distancias
(mediana + percentiles), no sólo el % bajo umbral. Criterio: condición (2) del falsador congelado
(>80% → muerte por redundancia), tolerancia 10 bps, umbral 80% — IDÉNTICOS.
"""

from __future__ import annotations

import glob
import zipfile
from pathlib import Path

from src.crypto import volume_profile as vp

AGG_DIR = "data/raw_crypto/futures/um/daily/aggTrades"
KLINES_DIR = "data/raw_crypto/futures/um/monthly/klines"
HOLDOUT_START = "2024-03-01"
TOL_BPS = 10.0
KL_COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time",
           "quote_volume", "count", "tbv", "tbqv", "ignore"]


def _daily_closes(symbol):
    """{date 'YYYY-MM-DD': close} continuo, desde los klines 1d mensuales."""
    import pandas as pd

    frames = []
    for z in sorted(glob.glob(f"{KLINES_DIR}/{symbol}/1d/{symbol}-1d-*.zip")):
        with zipfile.ZipFile(z) as zf, zf.open(zf.namelist()[0]) as fh:
            first = fh.readline().decode()
        hdr = 0 if "open_time" in first else None
        with zipfile.ZipFile(z) as zf, zf.open(zf.namelist()[0]) as fh:
            frames.append(pd.read_csv(fh, names=KL_COLS, header=hdr, usecols=["open_time", "close"]))
    df = pd.concat(frames, ignore_index=True).drop_duplicates("open_time").sort_values("open_time")
    df["date"] = pd.to_datetime(df["open_time"], unit="ms").dt.strftime("%Y-%m-%d")
    df = df.set_index("date")["close"].astype(float)
    return df


def _sma_boll(closes):
    """SMA20 y Bollinger(20,2σ) por fecha (usando 20 cierres hasta e incluyendo el día)."""
    sma = closes.rolling(20).mean()
    std = closes.rolling(20).std(ddof=0)
    return sma, sma + 2 * std, sma - 2 * std


def main():
    import numpy as np

    daily = {s: _daily_closes(s) for s in ("BTCUSDT", "ETHUSDT")}
    ind = {s: _sma_boll(daily[s]) for s in daily}

    rows = []
    for sym in ("BTCUSDT", "ETHUSDT"):
        sma, bsup, binf = ind[sym]
        for f in sorted(glob.glob(f"{AGG_DIR}/{sym}/{sym}-aggTrades-*.zip")):
            date = Path(f).stem.replace(f"{sym}-aggTrades-", "")
            if date >= HOLDOUT_START or date not in sma.index or np.isnan(sma[date]):
                continue
            df = vp.read_agg_trades(f)
            p = vp.build_profile(df["price"].to_numpy(), df["quantity"].to_numpy())
            vwap = float((df["price"] * df["quantity"]).sum() / df["quantity"].sum())
            mid = p.poc
            rows.append({
                "vah_boll": abs(p.vah - bsup[date]) / mid * 1e4,
                "val_boll": abs(p.val - binf[date]) / mid * 1e4,
                "poc_sma": abs(p.poc - sma[date]) / mid * 1e4,
                "poc_vwap": abs(p.poc - vwap) / mid * 1e4,
            })

    n = len(rows)
    print(f"# H008 — Coincidencia BIEN EMPAREJADA (interior vs interior), {n} días-instrumento in-sample\n")
    if n == 0:
        print("Sin datos."); return

    def ci(k):
        p = k / n; se = (p * (1 - p) / n) ** 0.5
        return p, max(0, p - 1.96 * se), min(1, p + 1.96 * se)

    comps = [("VAH ≈ Bollinger_sup", "vah_boll"), ("VAL ≈ Bollinger_inf", "val_boll"),
             ("POC ≈ SMA(20)", "poc_sma"), ("POC ≈ VWAP(24h)", "poc_vwap")]
    print("| comparación | ≤10bps | % | IC95 | mediana | p25 | p75 | p90 |")
    print("|---|---|---|---|---|---|---|---|")
    any_hit = [False] * n
    for name, key in comps:
        d = np.array([r[key] for r in rows])
        hit = d <= TOL_BPS
        for i in range(n):
            any_hit[i] = any_hit[i] or hit[i]
        p, lo, hi = ci(int(hit.sum()))
        q = np.percentile(d, [25, 50, 75, 90])
        print(f"| {name} | {int(hit.sum())}/{n} | {p:.0%} | [{lo:.0%},{hi:.0%}] | "
              f"{q[1]:.0f} | {q[0]:.0f} | {q[2]:.0f} | {q[3]:.0f} | (bps)")
    p, lo, hi = ci(sum(any_hit))
    print(f"| **cualquiera** | {sum(any_hit)}/{n} | **{p:.0%}** | [{lo:.0%},{hi:.0%}] | — | — | — | — |")

    print("\nATENCIÓN POC vs VWAP: ambos son precio ponderado por volumen sobre 24h.")
    poc_vwap = np.array([r["poc_vwap"] for r in rows])
    pv, plo, phi = ci(int((poc_vwap <= TOL_BPS).sum()))
    print(f"  POC≈VWAP: {pv:.0%} [{plo:.0%},{phi:.0%}], mediana {np.median(poc_vwap):.0f} bps")

    _, elo, ehi = ci(sum(any_hit))
    print()
    if elo > 0.80:
        print("VEREDICTO (2): coincidencia >80% con IC que no cruza → H008 MUERTA por REDUNDANCIA.")
    elif ehi < 0.80:
        print("VEREDICTO (2): coincidencia <80% con IC que no cruza → (2) NO dispara; adelante Bloque 4.")
    else:
        print("VEREDICTO (2): IC cruza 80% → no concluyente; decisión explícita / más días.")


if __name__ == "__main__":
    main()
