"""ofi_validate_full.py — Bloque A: validación completa del OFI en 4 días/regímenes.

Deliverable #1 (tabla por día) + #2 (verificación de unidades) + #6 (GB/tiempo).

Regímenes elegidos por vol realizada ANTES de correr el OFI (klines 1m, Jan-Mar 2024):
  2024-02-03 range/baja (rv 1.0%/día) · 2024-02-12 normal (2.6%) ·
  2024-03-05 alta (7.6%) · 2024-01-02 normal-atípico post-Año-Nuevo (3.1%).
"""

from __future__ import annotations

import time
import zipfile
from pathlib import Path

import pandas as pd

from src.crypto import calibrate, ingest, ofi

DAYS = [
    ("2024-01-02", "normal (post-NY, atípico)"),
    ("2024-02-03", "range/baja vol"),
    ("2024-02-12", "normal"),
    ("2024-03-05", "alta vol"),
]


def _agg(path):
    cols = ["agg_trade_id", "price", "quantity", "first_trade_id",
            "last_trade_id", "transact_time", "is_buyer_maker"]
    with zipfile.ZipFile(path) as z:
        with z.open(z.namelist()[0]) as fh:
            return pd.read_csv(fh, names=cols, header=0)


def run_day(date, dt_s=10):
    bt = ingest.RAW_ROOT / f"{ingest.daily_key('futures/um','bookTicker','BTCUSDT',date)}.zip"
    at = ingest.RAW_ROOT / f"{ingest.daily_key('futures/um','aggTrades','BTCUSDT',date)}.zip"
    gb = (bt.stat().st_size + at.stat().st_size) / 1e9
    t0 = time.time()
    df = ingest.read_book_ticker(bt)
    grid = ofi.build_grid(df, dt_s=dt_s)
    grid_excl = ofi.build_grid(df, dt_s=dt_s, exclude_price_changing=True)
    ti = ofi.trade_imbalance(_agg(at), dt_s=dt_s)

    res = calibrate.calibrate(grid, grid_excl=grid_excl,
                              trade_imb=calibrate.grid_with_trade_imbalance(grid, ti))
    joint = calibrate.joint_regressions(calibrate.add_trade_imbalance(grid, ti))
    units = calibrate.estimate_c_and_units(grid)
    secs = time.time() - t0

    passes = (res.mean_r2_ofi > 0.40 and res.mean_r2_ofi > (res.mean_r2_ti or 1)
              and (units["lambda_loglog"] > 0)  # β∝1/depth (pendiente log-log negativa → λ>0)
              and (res.mean_r2_excl_price_changing or 0) > 0.20)
    return {"date": date, "r2_ofi": res.mean_r2_ofi, "r2_ti": res.mean_r2_ti,
            "r2_joint": joint["r2_joint"], "t_O": joint["t_theta_O"], "t_T": joint["t_theta_T"],
            "pct_sig_T": joint["pct_sig_T"], "pct_sig_O": joint["pct_sig_O"],
            "slope": -units["lambda_loglog"], "c": units["c_lambda1"],
            "r2_excl": res.mean_r2_excl_price_changing, "passes": passes,
            "units": units, "gb": gb, "secs": secs}


def main():
    rows, total_gb, total_s = [], 0.0, 0.0
    print("Procesando 4 días (esto tarda; ~18M filas/día)...\n")
    for date, regime in DAYS:
        r = run_day(date)
        r["regime"] = regime
        rows.append(r)
        total_gb += r["gb"]; total_s += r["secs"]
        print(f"  {date} [{regime}]: R²_OFI {r['r2_ofi']:.3f}  R²_TI {r['r2_ti']:.3f}  "
              f"R²_joint {r['r2_joint']:.3f}  t(θ_O) {r['t_O']:.1f}  t(θ_T) {r['t_T']:.1f}  "
              f"%sigT {r['pct_sig_T']:.0%}  ĉ {r['c']:.3f}  {'PASA' if r['passes'] else 'NO'}"
              f"  ({r['gb']:.2f}GB {r['secs']:.0f}s)")

    # Deliverable #1: tabla markdown
    print("\n## Tabla de validación completa (Bloque A)\n")
    hdr = ("| fecha | régimen | R²_OFI | R²_TI | R²_conj | t(θ_O) | t(θ_T) | %sig(θ_T) | "
           "pendiente | ĉ | R² excl.precio | ¿pasa? |")
    print(hdr); print("|" + "---|" * 12)
    for r in rows:
        print(f"| {r['date']} | {r['regime']} | {r['r2_ofi']:.3f} | {r['r2_ti']:.3f} | "
              f"{r['r2_joint']:.3f} | {r['t_O']:.1f} | {r['t_T']:.1f} | {r['pct_sig_T']:.0%} | "
              f"{r['slope']:.2f} | {r['c']:.3f} | {r['r2_excl']:.3f} | "
              f"{'SÍ' if r['passes'] else 'NO'} |")

    # Deliverable #2: verificación de unidades (día normal representativo)
    print("\n## Verificación de unidades\n")
    for r in rows:
        u = r["units"]
        print(f"- {r['date']}: β medio {u['beta_mean']:.3f} → profundidad implícita "
              f"(c=0.5) {u['implied_depth_c05']:.2f} BTC · profundidad MEDIDA "
              f"{u['depth_measured']:.2f} BTC · factor {u['discrepancy_factor']:.1f}× "
              f"· ĉ(λ=1) {u['c_lambda1']:.3f}")

    # Deliverable #6
    print(f"\n## Cómputo: {total_gb:.2f} GB procesados, {total_s:.0f}s total "
          f"({total_s/len(rows):.0f}s/día).")


if __name__ == "__main__":
    main()
