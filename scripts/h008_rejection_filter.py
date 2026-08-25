"""h008_rejection_filter.py — H008: duty REAL tras el filtro de rechazo (sin backtest).

Mide UNA cosa: de los edge-touch, cuántos sobreviven al filtro de RECHAZO de la ficha (el mid
re-entra al área de valor del día PREVIO dentro de K=3 barras de 1 min). Requiere klines 1m
(ligeros). Luego recalcula duty real, Sharpe activo requerido, rt/día, requerido bruto cripto
y T efectiva. NO hay estrategia, ni benchmark nulo, ni Δ Sharpe.
"""

from __future__ import annotations

import csv
import glob
import zipfile
from pathlib import Path

from src import costs_model as cm
from src.crypto import cost_model as ccm

KL = "data/raw_crypto/futures/um/monthly/klines"
SUMMARY = "results/crypto/h008_daily_summary.csv"
K_BARS = 3
INS_START, HOLDOUT = "2022-09-01", "2024-03-01"
KL_COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time",
           "quote_volume", "count", "tbv", "tbqv", "ignore"]


def _read_klines(sym, interval, usecols):
    import pandas as pd

    fr = []
    for z in sorted(glob.glob(f"{KL}/{sym}/{interval}/{sym}-{interval}-*.zip")):
        with zipfile.ZipFile(z) as zf, zf.open(zf.namelist()[0]) as fh:
            first = fh.readline().decode()
        h = 0 if "open_time" in first else None
        with zipfile.ZipFile(z) as zf, zf.open(zf.namelist()[0]) as fh:
            fr.append(pd.read_csv(fh, names=KL_COLS, header=h, usecols=usecols))
    df = pd.concat(fr).drop_duplicates("open_time").sort_values("open_time")
    df["date"] = pd.to_datetime(df["open_time"], unit="ms").dt.strftime("%Y-%m-%d")
    return df


def _balance_days(sym):
    import numpy as np

    d = _read_klines(sym, "1d", ["open_time", "high", "low", "close"]).set_index("date")
    tr = np.maximum(d.high - d.low, np.maximum((d.high - d.close.shift()).abs(),
                                               (d.low - d.close.shift()).abs()))
    atr = tr.rolling(14).mean()
    return ((d.high - d.low) / atr < 1.0), atr


def main():
    import numpy as np

    prof = {}
    for r in csv.DictReader(open(SUMMARY)):
        prof[(r["sym"], r["date"])] = (float(r["vah"]), float(r["val"]))

    total_days = edge = rejection = 0
    for sym in ("BTCUSDT", "ETHUSDT"):
        balance, atr = _balance_days(sym)
        bars = _read_klines(sym, "1m", ["open_time", "high", "low", "close"])
        by_day = {dt: g for dt, g in bars.groupby("date")}
        dates = [x for x in sorted(by_day) if INS_START <= x < HOLDOUT and x in atr.index and not np.isnan(atr[x])]
        prev = {dates[i]: dates[i - 1] for i in range(1, len(dates))}
        for dt in dates:
            total_days += 1
            pd_ = prev.get(dt)
            if pd_ is None or not balance.get(pd_, False) or (sym, pd_) not in prof:
                continue
            vah, val = prof[(sym, pd_)]
            g = by_day[dt].sort_values("open_time")
            hi = g["high"].to_numpy(); lo = g["low"].to_numpy(); cl = g["close"].to_numpy()
            # primer cruce fuera del VA previo
            above = np.where(hi >= vah)[0]
            below = np.where(lo <= val)[0]
            i_above = above[0] if len(above) else 10**9
            i_below = below[0] if len(below) else 10**9
            if min(i_above, i_below) == 10**9:
                continue
            edge += 1
            if i_above <= i_below:
                i = i_above
                rej = np.any(cl[i + 1:i + 1 + K_BARS] < vah)      # re-entra (baja del VAH)
            else:
                i = i_below
                rej = np.any(cl[i + 1:i + 1 + K_BARS] > val)      # re-entra (sube del VAL)
            if rej:
                rejection += 1

    duty = rejection / total_days
    rt_day = rejection / total_days                                # 1 round-trip por episodio
    activo_req = cm.sharpe_activo_requerido(duty)
    bruto_req = ccm.sharpe_bruto_requerido_cripto(rt_day, fraccion_maker=1.0, cruces_funding_por_dia=0)
    t_eff_lo, t_eff_hi = rejection * (1.11 / 2), rejection

    print(f"# H008 — Duty REAL tras el filtro de rechazo (K={K_BARS} barras de 1 min)\n")
    print(f"días-instrumento in-sample: {total_days}")
    print(f"edge-touch (fuera del VA previo, día de balance): {edge} (duty edge {edge/total_days:.0%})")
    print(f"RECHAZO confirmado (mid re-entra al VA en ≤{K_BARS} barras): {rejection} (duty {duty:.0%})")
    print(f"supervivencia del rechazo: {rejection/edge:.0%} de los edge-touch\n")
    print("## Listón recalculado sobre el duty REAL")
    print(f"- duty real: {duty:.0%}  (a priori en la ficha: 20%)")
    print(f"- Sharpe ACTIVO requerido (0.40/√duty+0.245): {activo_req:.3f}  (a priori 20% → 1.139)")
    print(f"- round-trips/día reales: {rt_day:.2f}")
    print(f"- requerido bruto cripto (maker, funding evitado, {rt_day:.2f} rt/día): {bruto_req:.3f}")
    print(f"- T efectiva (episodios supervivientes, descuento ρ0.8): ~{t_eff_lo:.0f}-{t_eff_hi:.0f}")
    print()
    if t_eff_hi < 150 and t_eff_lo < 150:
        print(f"T efectiva < 150 → DECISIÓN EXPLÍCITA NECESARIA (ampliar muestra / underpowered / parar).")
    else:
        print(f"T efectiva ≥ 150 → poder suficiente; procede el Bloque 4 con el listón real.")


if __name__ == "__main__":
    main()
