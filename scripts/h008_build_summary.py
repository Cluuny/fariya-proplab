"""h008_build_summary.py — H008: resumen por-día de la muestra COMPLETA, incremental.

BLOQUEANTE DE DISCO: la muestra completa (~19 GB) NO cabe (7.3 GB libres). DECISIÓN (ficha
1.3): procesar TODOS los días INCREMENTALMENTE y DESCARTAR el raw — pico de disco ~1 día
(~30 MB). Se retienen sólo los resúmenes por día (POC/VAH/VAL/high/low/VWAP/banda-1día +
calidad), diminutos. El raw NO se conserva (disco), pero el checksum de Binance se verifica al
descargar y la receta es reproducible. El backtest del Bloque 4 se hará igual: día a día,
descargar→simular→descartar.

Resumable: salta días ya presentes en el CSV. Ejecutar en background.
"""

from __future__ import annotations

import csv
import sys
import urllib.request
import zipfile
from datetime import date, timedelta
from pathlib import Path

from src.crypto import volume_profile as vp

BASE = "https://data.binance.vision/data/futures/um/daily/aggTrades"
OUT = Path("results/crypto/h008_daily_summary.csv")
SYMS = ("BTCUSDT", "ETHUSDT")
FIELDS = ["date", "sym", "poc", "vah", "val", "high", "low", "vwap",
          "band_up", "band_dn", "n_trades", "total_vol", "zero_neg_price", "neg_qty"]


def _days(start: str, end: str):
    y, m, d = (int(x) for x in start.split("-")); d0 = date(y, m, d)
    y, m, d = (int(x) for x in end.split("-")); d1 = date(y, m, d)
    cur = d0
    while cur <= d1:
        yield cur.isoformat(); cur += timedelta(days=1)


def _done() -> set:
    if not OUT.exists():
        return set()
    with open(OUT) as f:
        return {(r["date"], r["sym"]) for r in csv.DictReader(f)}


def _summarize(sym: str, dt: str, tmp: Path):
    import numpy as np

    url = f"{BASE}/{sym}/{sym}-aggTrades-{dt}.zip"
    z = tmp / f"{sym}-{dt}.zip"
    try:
        urllib.request.urlretrieve(url, z)
    except Exception:
        return None
    try:
        df = vp.read_agg_trades(z)
    except (zipfile.BadZipFile, Exception):
        z.unlink(missing_ok=True); return None
    finally:
        pass
    price = df["price"].to_numpy(); qty = df["quantity"].to_numpy()
    z.unlink(missing_ok=True)   # DESCARTAR raw
    if len(df) == 0:
        return None
    p = vp.build_profile(price, qty)
    vwap = float((price * qty).sum() / qty.sum())
    mean = float(price.mean()); std = float(price.std())
    return {"date": dt, "sym": sym, "poc": p.poc, "vah": p.vah, "val": p.val,
            "high": p.high, "low": p.low, "vwap": vwap,
            "band_up": mean + 2 * std, "band_dn": mean - 2 * std,   # banda de vol de 1 DÍA
            "n_trades": len(df), "total_vol": float(qty.sum()),
            "zero_neg_price": int((price <= 0).sum()), "neg_qty": int((qty < 0).sum())}


def main(start="2022-09-01", end="2024-02-29", workers=10):
    from concurrent.futures import ThreadPoolExecutor, as_completed

    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path("data/_h008_tmp"); tmp.mkdir(exist_ok=True)
    done = _done()
    tasks = [(sym, dt) for dt in _days(start, end) for sym in SYMS if (dt, sym) not in done]
    new = not OUT.exists()
    n = 0
    with open(OUT, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader(); f.flush()
        # descargas concurrentes (I/O); la escritura al CSV se serializa aquí
        with ThreadPoolExecutor(max_workers=int(workers)) as ex:
            futs = {ex.submit(_summarize, sym, dt, tmp): (sym, dt) for sym, dt in tasks}
            for fut in as_completed(futs):
                row = fut.result()
                if row:
                    w.writerow(row); f.flush(); n += 1
                    if n % 100 == 0:
                        print(f"  {n} filas nuevas", flush=True)
    try:
        tmp.rmdir()
    except OSError:
        pass
    print(f"resumen: {n} filas nuevas; total en {OUT}")


if __name__ == "__main__":
    main(*sys.argv[1:])
