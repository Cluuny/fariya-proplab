"""cot_diagnostic.py — COT coverage + available duty cycle (Bloque 2.4/2.5).

Coverage with the Brent criterion (KILL >25% missing weeks) and, per instrument, the
DUTY CYCLE available if a strategy trades only positioning extremes (rolling-percentile
of net-spec beyond 10/90 and 5/95). That duty cycle sets the required gross Sharpe
(costs_model.sharpe_bruto_requerido_duty). No hypothesis pre-registered.

    uv run python scripts/cot_diagnostic.py
"""

from __future__ import annotations

import pandas as pd

from src import costs_model, cot


def diagnostic() -> pd.DataFrame:
    rows = []
    for inst in cot.COT_CONTRACTS:
        df = cot.load_cot(inst)
        dd = pd.to_datetime(df["date"])
        mod = dd[dd >= "2000-01-01"]
        exp = int((mod.max() - mod.min()).days / 7) + 1 if len(mod) > 1 else 0
        miss = 1 - len(mod) / exp if exp else 1.0
        ns = df["net_spec"].dropna()
        roll = ns.rolling(156, min_periods=52).apply(lambda x: x.rank(pct=True).iloc[-1], raw=False)
        duty10 = float(((roll <= 0.10) | (roll >= 0.90)).mean())
        duty05 = float(((roll <= 0.05) | (roll >= 0.95)).mean())
        rows.append({
            "inst": inst, "desde": str(dd.min().date()), "hasta": str(dd.max().date()),
            "semanas": len(df), "falta%": round(miss * 100, 1),
            "duty_10_90": round(duty10 * 100, 1), "duty_5_95": round(duty05 * 100, 1),
            "AC1": round(float(ns.autocorr(1)), 2),
            "req_gross": round(costs_model.sharpe_bruto_requerido_duty(duty10), 3),
            "cob": "KILL" if miss > 0.25 else "PASS",
        })
    return pd.DataFrame(rows)


def main() -> int:
    r = diagnostic()
    pd.set_option("display.width", 160)
    print(r.to_string(index=False))
    print("\nDuty cycle disponible ~20-30% (p10/90) → gross requerido ~0.45 (vs 0.64 always-in).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
