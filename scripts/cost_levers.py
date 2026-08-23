"""cost_levers.py — the two cost levers (Bloque B). Characterizes the cost engine;
NOT a new attempt at H001/H007 (no verdicts, no intentos touched).

  B.1 gross sweep — scale tsmom weights to a target gross; gross & net Sharpe.
  B.2 holding sweep — rebalance monthly/bimonthly/quarterly; turnover, margin,
      spread, net Sharpe.

Finding (see docs/cost_floor.md): net Sharpe is scale-invariant (gross is not a
lever), and margin is holding-invariant (holding only trims the tiny spread).

    uv run python scripts/cost_levers.py
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src import config, engine, rates, signals

UNIVERSE = list(config.INSTRUMENTS)
START, END = "2015-01-01", "2023-08-16"


def _setup():
    px = pd.DataFrame({c: pd.read_parquet(config.DATA_CLEAN / f"{c}.parquet")["close"]
                       for c in UNIVERSE}).loc[:END]
    cm = rates.carry_matrix(px.index, UNIVERSE)
    return px, cm


def gross_sweep(px, cm):
    w0 = signals.tsmom(px)
    live = w0.abs().sum(axis=1) > 0
    s0 = max(pd.Timestamp(START), w0.index[live][0])
    g0 = w0.abs().sum(axis=1)
    gross_s = engine.sharpe(engine.backtest(px, w0, apply_costs=False).loc[s0:])
    rows = []
    for G in np.arange(0.5, 2.51, 0.25):
        w = w0.mul((G / g0.where(g0 > 0, np.nan)).fillna(0.0), axis=0)
        net = engine.backtest(px, w, costs=config.COSTS, carry_matrix=cm).loc[s0:]
        rows.append((round(float(G), 2), gross_s, engine.sharpe(net)))
    return rows


def holding_sweep(px, cm):
    live = signals.tsmom(px).abs().sum(axis=1) > 0
    s0 = max(pd.Timestamp(START), signals.tsmom(px).index[live][0])
    margins = pd.Series({c: config.COSTS[c].swap_margin for c in UNIVERSE})
    tr = pd.Series({c: config.COSTS[c].spread + config.COSTS[c].slippage for c in UNIVERSE})
    rows = []
    for freq, lbl in [("BMS", "mensual"), ("2BMS", "bimestral"), ("QS", "trimestral")]:
        w = signals.tsmom(px, rebalance=freq)
        prev = w.shift(1).fillna(0.0)
        dturn = (w - w.shift(1).fillna(0.0)).abs()
        m_d = prev.abs().mul(margins, axis=1).sum(axis=1).loc[s0:]
        sp_d = dturn.mul(tr, axis=1).sum(axis=1).loc[s0:]
        turn = dturn.sum(axis=1).loc[s0:]
        bpy = engine.bars_per_year(m_d)
        net = engine.sharpe(engine.backtest(px, w, costs=config.COSTS, carry_matrix=cm).loc[s0:])
        rows.append((lbl, turn.sum() / (len(turn) / bpy), m_d.mean() * bpy, sp_d.mean() * bpy, net))
    return rows


def main() -> int:
    px, cm = _setup()
    print("B.1 GROSS SWEEP (gross → bruto/neto):")
    for G, gr, nt in gross_sweep(px, cm):
        print(f"  G={G:>4} bruto={gr:+.3f} neto={nt:+.3f}")
    print("\nB.2 HOLDING SWEEP:")
    for lbl, t, m, s, n in holding_sweep(px, cm):
        print(f"  {lbl:>10} turnover={t:5.1f}× margen={m*100:5.2f}% spread={s*100:4.2f}% neto={n:+.3f}")
    print("\nVer docs/cost_floor.md: gross NO es palanca (neto invariante); "
          "holding sólo recorta el spread. El suelo es margen-dominado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
