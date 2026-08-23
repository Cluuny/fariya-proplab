"""audit_universe.py — Universe coverage audit (Bloque 1).

Measures the REAL Dukascopy daily coverage of candidate instruments with the same
criterion that killed BRENT: missing business days within each instrument's own
[first, last] range (Brent had ~37% missing, 166 bars/yr → unusable).

Two views per instrument:
  - full history: first→last, obs, missing business days, missing%, bars/year
  - modern window (2015+): the coverage that actually matters if we trade post-2011,
    since early-2000s CFD sparsity inflates the full-history number; plus staleness
    (days since last bar — a feed that stopped is not live-tradeable).

Usage (analysis only, over a dir of dukascopy-node CSVs):
    uv run python scripts/audit_universe.py --dir <csv_dir>

Download first with dukascopy-node (one CSV per symbol), e.g.:
    npx -y dukascopy-node -i eurjpy -from 2003-01-01 -to <today> -t d1 -f csv -dir <csv_dir>
"""

from __future__ import annotations

import argparse
import glob
import os

import pandas as pd

KILL_FRAC = 0.25          # Brent territory (~37%); >25% missing = unusable
CAUTION_FRAC = 0.10       # 10-25% = usable with care
MODERN_WINDOW = "2015-01-01"
STALE_DAYS = 40           # a daily feed silent >40 days is effectively delisted


def _load(path: str) -> pd.DataFrame | None:
    if sum(1 for _ in open(path)) <= 1:
        return None
    df = pd.read_csv(path)
    if "timestamp" not in df.columns:
        return None
    df["date"] = pd.to_datetime(df["timestamp"], unit="ms")
    df = df[df["date"].dt.dayofweek < 5]          # drop weekends (loaders.clean)
    return df.drop_duplicates("date").sort_values("date")


def _coverage(dates: pd.Series) -> tuple[int, int, float, float]:
    d0, d1 = dates.min(), dates.max()
    exp = len(pd.bdate_range(d0, d1))
    obs = len(dates)
    frac = (exp - obs) / exp if exp else 1.0
    bpy = obs / ((d1 - d0).days / 365.25) if d1 > d0 else 0.0
    return obs, exp - obs, frac, bpy


def audit(csv_dir: str, today: str) -> pd.DataFrame:
    end = pd.Timestamp(today)
    best: dict[str, tuple[str, int]] = {}
    for f in glob.glob(os.path.join(csv_dir, "*-d1-*.csv")):
        sym = os.path.basename(f).split("-d1-")[0]
        n = sum(1 for _ in open(f))
        if sym not in best or n > best[sym][1]:
            best[sym] = (f, n)

    rows = []
    for sym, (f, _) in sorted(best.items()):
        df = _load(f)
        if df is None or df.empty:
            rows.append({"symbol": sym, "verdict": "SIN DATOS"})
            continue
        obs, miss, frac, bpy = _coverage(df["date"])
        rec = df[df["date"] >= MODERN_WINDOW]
        if rec.empty:
            m_frac, m_last, m_obs = 1.0, None, 0
        else:
            _, _, m_frac, _ = _coverage(rec["date"])
            m_last, m_obs = rec["date"].max(), len(rec)
        stale = (end - df["date"].max()).days
        verdict = "PASS" if frac < CAUTION_FRAC else ("CAUTION" if frac < KILL_FRAC else "KILL")
        rows.append({
            "symbol": sym,
            "desde": str(df["date"].min().date()), "hasta": str(df["date"].max().date()),
            "obs": obs, "miss": miss, "miss%": round(frac * 100, 1), "bpy": round(bpy),
            "miss15%": round(m_frac * 100, 1) if m_obs else None,
            "stale_d": stale, "verdict": verdict,
        })
    return pd.DataFrame(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True, help="directory of dukascopy-node d1 CSVs")
    ap.add_argument("--today", default="2026-08-14", help="reference date for staleness")
    args = ap.parse_args()
    r = audit(args.dir, args.today)
    pd.set_option("display.max_rows", 80, "display.width", 160)
    print(r.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
