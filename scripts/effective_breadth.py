"""effective_breadth.py — Effective breadth of the universe (Bloque 2 metric).

The plan's progress metric is NOT the raw instrument count but the EFFECTIVE
number of independent bets: N_eff = (Σλ)² / Σλ² over the eigenvalues λ of the
daily-return correlation matrix (participation ratio). Correlated instruments
(EURJPY ≈ spanned by EUR/JPY majors; US30 ≈ SPX500) add far less than 1 to N_eff.

By Grinold-Kahn (IR ≈ IC·√BR), the Sharpe ceiling scales with √N_eff, so N_eff is
what actually moves the achievable Sharpe — the number to track when expanding.

    uv run python scripts/effective_breadth.py [--start 2014-01-01]
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from src import config

OLD_9 = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "XAUUSD", "SPX500", "GER40", "JPN225"]


def _returns(cols: list[str]) -> pd.DataFrame:
    px = pd.DataFrame(
        {c: pd.read_parquet(config.DATA_CLEAN / f"{c}.parquet")["close"] for c in cols}
    )
    return px.pct_change()


def n_eff(corr: np.ndarray) -> float:
    ev = np.linalg.eigvalsh(corr)
    ev = ev[ev > 0]
    return float((ev.sum() ** 2) / (ev ** 2).sum())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2014-01-01")
    args = ap.parse_args()

    new = list(config.INSTRUMENTS)
    # Common dates where ALL current-universe instruments trade → identical basis.
    dates = _returns(new).loc[args.start:].dropna(how="any").index

    def neff_on(cols: list[str]) -> float:
        return n_eff(_returns(cols).reindex(dates).corr().to_numpy())

    ne_old, ne_new = neff_on(OLD_9), neff_on(new)
    print(f"Ventana: {dates.min().date()} → {dates.max().date()}  ({len(dates)} días comunes)")
    print(f"ANTES  (9):  N_eff = {ne_old:.2f}")
    print(f"DESPUÉS ({len(new)}): N_eff = {ne_new:.2f}   "
          f"(+{ne_new - ne_old:.2f}, x{ne_new / ne_old:.2f})")
    print(f"Techo de Sharpe (√BR): x{(ne_new / ne_old) ** 0.5:.2f}")

    print("\nAporte marginal de cada instrumento nuevo (N_eff de los 9 + ese uno):")
    for c in [x for x in new if x not in OLD_9]:
        d = neff_on(OLD_9 + [c]) - ne_old
        flag = "  <-- redundante/negativo" if d < 0.1 else ""
        print(f"  +{c:7}: Δ {d:+.2f}{flag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
