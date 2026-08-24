"""ofi_decay.py — Bloque B: curva de decaimiento predictivo + cruce con el suelo de costes.

Produce el deliverable #3 (tabla por horizonte), #4 (datos para el gráfico), el veredicto
(#5) y GB/tiempo (#6). Poolea los 4 días validados.
"""

from __future__ import annotations

import time
from pathlib import Path

from src.crypto import decay, ingest, ofi

DAYS = ["2024-01-02", "2024-02-03", "2024-02-12", "2024-03-05"]


def main():
    t0 = time.time()
    gb = sum((ingest.RAW_ROOT / f"{ingest.daily_key('futures/um','bookTicker','BTCUSDT',d)}.zip").stat().st_size
             for d in DAYS) / 1e9

    # cap por día (memoria acotada): varias horas × 4 regímenes → decenas de millones de
    # eventos poolados, sobra para la curva de decaimiento. Full-day reproducible offline.
    import os
    NROWS = int(os.environ.get("DECAY_NROWS", "7000000"))

    def stream():
        for d in DAYS:
            bt = ingest.RAW_ROOT / f"{ingest.daily_key('futures/um','bookTicker','BTCUSDT',d)}.zip"
            df = ingest.read_book_ticker(bt, nrows=NROWS)
            print(f"  {d}: {len(df):,} filas (cap {NROWS:,})", flush=True)
            ev = ofi.compute_events(df)
            del df
            yield ev
            del ev

    rows = decay.decay_curve(stream())
    verd = decay.verdict(rows)
    secs = time.time() - t0

    def hlabel(s):
        return f"{s}s" if s < 60 else f"{s//60}min"

    lines = ["# Tabla de decaimiento (Bloque B) — pool de 4 días", "",
             "| horizonte | R²_contemp | R²_predictivo | IC_pred | IC95 | n_indep | "
             "Sharpe implícito | rt/día | listón maker | listón taker | BRECHA(maker) |",
             "|" + "---|" * 11]
    for r in rows:
        lines.append(
            f"| {hlabel(r.horizon_s)} | {r.r2_contemp:.3f} | {r.r2_pred:.4f} | {r.ic_pred:+.3f} | "
            f"[{r.ic_lo:+.3f},{r.ic_hi:+.3f}] | {r.n_indep:,} | {r.implied_sharpe:.2f} | "
            f"{r.rt_per_day:,.0f} | {r.floor_maker:,.1f} | {r.floor_taker:,.1f} | "
            f"{r.gap_maker:+.2f} |")
    lines += ["", "## Datos del gráfico (R² predictivo vs horizonte, con IC de IC→R²)",
              "horizonte_s,r2_pred,ic_lo2,ic_hi2"]
    for r in rows:
        lines.append(f"{r.horizon_s},{r.r2_pred:.6f},{max(r.ic_lo,0)**2:.6f},{r.ic_hi**2:.6f}")
    lines += ["", f"## VEREDICTO (B.4): **{verd['estado']}**",
              f"- mejor horizonte: {hlabel(verd['mejor_horizonte_s'])}; "
              f"Sharpe implícito {verd['mejor_implied_sharpe']:.2f} vs listón maker "
              f"{verd['mejor_floor_maker']:,.1f} → brecha {verd['mejor_gap_maker']:+.2f}",
              f"- GB procesados: {gb:.2f} · tiempo {secs:.0f}s"]

    report = "\n".join(lines) + "\n"
    print(report)
    out = Path("results/crypto/blockB_decay.md")
    out.write_text(report)
    # ASCII sparkline del R² predictivo
    _ascii_plot(rows)


def _ascii_plot(rows):
    print("\nR² predictivo vs horizonte (escala log-ish):")
    mx = max(r.r2_pred for r in rows) or 1e-9
    for r in rows:
        h = f"{r.horizon_s}s" if r.horizon_s < 60 else f"{r.horizon_s//60}min"
        bar = "█" * int(40 * r.r2_pred / mx)
        print(f"  {h:>6} | {bar} {r.r2_pred:.4f}")


if __name__ == "__main__":
    main()
