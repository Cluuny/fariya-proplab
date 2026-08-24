"""ofi_calibrate.py — runner de Bloque 2: correr el test de calibración del OFI.

Uso:
    python -m scripts.ofi_calibrate --symbol BTCUSDT --date 2024-01-02 [--dt 10]

Lee el bookTicker (y el aggTrades si está, para la comparación con trade imbalance),
construye la rejilla de Δt segundos, corre las regresiones por media hora con SE de White,
imprime la tabla de aceptación y guarda el reporte en results/crypto/.
"""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

import pandas as pd

from src.crypto import calibrate, ingest, ofi


def _load_agg_trades(path: Path):
    cols = ["agg_trade_id", "price", "quantity", "first_trade_id",
            "last_trade_id", "transact_time", "is_buyer_maker"]
    with zipfile.ZipFile(path) as z:
        with z.open(z.namelist()[0]) as fh:
            return pd.read_csv(fh, names=cols, header=0)


def main(argv=None):
    p = argparse.ArgumentParser(description="Calibración del OFI (Bloque 2)")
    p.add_argument("--symbol", default="BTCUSDT")
    p.add_argument("--date", default="2024-01-02")
    p.add_argument("--dt", type=int, default=10, help="Δt en segundos")
    args = p.parse_args(argv)

    bt = ingest.RAW_ROOT / f"{ingest.daily_key('futures/um','bookTicker',args.symbol,args.date)}.zip"
    df = ingest.read_book_ticker(bt)
    grid = ofi.build_grid(df, dt_s=args.dt)
    grid_excl = ofi.build_grid(df, dt_s=args.dt, exclude_price_changing=True)

    grid_ti = None
    at = ingest.RAW_ROOT / f"{ingest.daily_key('futures/um','aggTrades',args.symbol,args.date)}.zip"
    if at.exists():
        ti = ofi.trade_imbalance(_load_agg_trades(at), dt_s=args.dt)
        grid_ti = calibrate.grid_with_trade_imbalance(grid, ti)

    res = calibrate.calibrate(grid, grid_excl=grid_excl, trade_imb=grid_ti)

    lines = [
        f"# Validación del OFI — {args.symbol} {args.date} (Δt={args.dt}s, OLS media hora, White SE)",
        "",
        f"- submuestras (medias horas): **{res.n_subsamples}**",
        f"- **R² medio OFI: {res.mean_r2_ofi:.3f}** (paper ~0.65; umbral aceptación >0.40)",
        f"- R² medio trade imbalance: {res.mean_r2_ti:.3f} (paper ~0.32)"
        if res.mean_r2_ti is not None else "- R² trade imbalance: (sin aggTrades)",
        f"- R² excluyendo eventos que cambian precio: {res.mean_r2_excl_price_changing:.3f} (paper 0.35-0.60)"
        if res.mean_r2_excl_price_changing is not None else "",
        f"- pendiente log-log β vs profundidad: {res.depth_loglog_slope:.3f} (~ −1 esperado)"
        if res.depth_loglog_slope is not None else "",
        f"- β medio: {res.mean_beta:.4e}; fracción con |t_White|>1.96: {res.frac_beta_significant:.0%}",
        "",
        "## Verificaciones",
        f"- R² > umbral: {res.checks['r2_ofi_gt_threshold']}",
        f"- (a) OFI mejor que trade imbalance (MÁS discriminante): {res.checks['a_ofi_beats_trade_imbalance']}",
        f"- (b) β inversa a la profundidad: {res.checks['b_beta_inverse_depth']}",
        f"- (c) al excluir eventos que cambian precio, R² baja pero se mantiene: {res.checks['c_excl_price_changing_holds']}",
        "",
        f"## VEREDICTO: {'PASA' if res.passes else 'NO PASA'} el Bloque 2",
    ]
    report = "\n".join(x for x in lines if x != "") + "\n"
    print(report)
    out = Path("results/crypto")
    out.mkdir(parents=True, exist_ok=True)
    (out / f"ofi_validation_{args.symbol}_{args.date}.md").write_text(report)


if __name__ == "__main__":
    main()
