"""run_h001.py — Run the H001 (TSMOM) verdict against the frozen contract.

Two samples reported separately; primary swap spec = 0.3 bp dictates the verdict,
0.0 and 1.0 bp are robustness diagnostics; marginal-zone [0.2, 0.4] triggers a
single robustness check (6-month lookback) with a deflated Sharpe. See
hypotheses/H001_tsmom.yaml (the contract — this script does NOT edit it).

    uv run python scripts/run_h001.py
"""

from __future__ import annotations

import dataclasses
import math

import pandas as pd

from src import config, engine, signals

# --- Samples (from the contract's universo_test) ---
SAMPLE_A = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "XAUUSD"]  # FX + gold
SAMPLE_B = list(config.INSTRUMENTS)  # all 9
EVAL_START = {"A": "2004-01-01", "B": "2015-01-01"}

SWAPS_BP = [0.0, 0.3, 1.0]          # daily, in basis points
PRIMARY_SWAP_BP = 0.3               # the verdict is dictated on this one
LOOKBACKS = {"primary": 12, "robustness": 6}
SUCCESS, FALSIFIER = 0.4, 0.2       # from metrica_exito / FALSADOR (frozen)


def _load(cols: list[str]) -> pd.DataFrame:
    return pd.DataFrame(
        {c: pd.read_parquet(config.DATA_CLEAN / f"{c}.parquet")["close"] for c in cols}
    )


def _costs_with_swap(cols: list[str], swap_bp: float) -> dict[str, config.CostModel]:
    swap = swap_bp * 1e-4
    cm = dataclasses.replace(config.DEFAULT_COST, swap=swap)
    return {c: cm for c in cols}


def _net_sharpe(prices, weights, cols, swap_bp, eval_start) -> tuple[float, str]:
    """Net Sharpe over the evaluation window (signal uses all prior history)."""
    net = engine.backtest(prices, weights, costs=_costs_with_swap(cols, swap_bp))
    live = weights.abs().sum(axis=1) > 0
    start = max(pd.Timestamp(eval_start), weights.index[live][0])
    sl = net.loc[start:]
    return engine.sharpe(sl), str(start.date())


def _expected_max_sharpe_null(sharpes: list[float]) -> float:
    """E[max of N Sharpes] under the null (Bailey-López de Prado).

    E[max] ≈ σ_SR·[(1-γ)·Z⁻¹(1-1/N) + γ·Z⁻¹(1-1/(N·e))], with γ = Euler-Mascheroni
    and σ_SR the std across the N trials' Sharpe estimates. The deflated Sharpe is
    the observed best minus this expected-max-under-null haircut.
    """
    n = len(sharpes)
    if n < 2:
        return 0.0
    gamma = 0.5772156649
    sd = pd.Series(sharpes).std(ddof=1)
    z1 = _norm_ppf(1 - 1.0 / n)
    z2 = _norm_ppf(1 - 1.0 / (n * math.e))
    return float(sd * ((1 - gamma) * z1 + gamma * z2))


def _norm_ppf(p: float) -> float:
    """Inverse standard-normal CDF (Acklam's rational approximation)."""
    a = [-3.969683028665376e01, 2.209460984245205e02, -2.759285104469687e02,
         1.383577518672690e02, -3.066479806614716e01, 2.506628277459239e00]
    b = [-5.447609879822406e01, 1.615858368580409e02, -1.556989798598866e02,
         6.680131188771972e01, -1.328068155288572e01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e00,
         -2.549732539343734e00, 4.374664141464968e00, 2.938163982698783e00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e00,
         3.754408661907416e00]
    pl, ph = 0.02425, 1 - 0.02425
    if p < pl:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > ph:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
           (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


def run_sample(name: str, cols: list[str], lookback: int) -> dict:
    prices = _load(cols)
    weights = signals.tsmom(prices, lookback_months=lookback)
    row = {}
    for swap in SWAPS_BP:
        sr, start = _net_sharpe(prices, weights, cols, swap, EVAL_START[name])
        row[swap] = sr
        row["_start"] = start
    return row


def main() -> int:
    print("=" * 72)
    print("H001 — Time-Series Momentum — VERDICT (contract frozen)")
    print("=" * 72)

    primary = {}  # sample -> {swap: sharpe}
    for name, cols in (("A", SAMPLE_A), ("B", SAMPLE_B)):
        r = run_sample(name, cols, LOOKBACKS["primary"])
        primary[name] = r
        label = "FX+gold 2004-2026" if name == "A" else "all-9 2015-2026"
        print(f"\nMuestra {name} ({label}), eval desde {r['_start']}, lookback 12m:")
        for swap in SWAPS_BP:
            tag = "  <-- PRIMARY" if swap == PRIMARY_SWAP_BP else ""
            print(f"    swap {swap:>3} bp/día : Sharpe neto = {r[swap]:+.3f}{tag}")

    print("\n" + "-" * 72)
    print(f"Expectativa comprometida (resultado_esperado): ~0.40, rango [0.25, 0.60]")
    print(f"Éxito: > {SUCCESS} · Falsador: < {FALSIFIER} (por muestra, sobre swap 0.3)")
    print("-" * 72)

    # Verdict per sample on the primary swap spec.
    verdicts = {}
    marginal = {}
    for name in ("A", "B"):
        sr = primary[name][PRIMARY_SWAP_BP]
        if sr >= SUCCESS:
            verdicts[name] = "viable"
        elif sr < FALSIFIER:
            verdicts[name] = "muerta"
        else:
            verdicts[name] = "marginal"
            marginal[name] = sr
        print(f"Veredicto Muestra {name}: {verdicts[name]} (Sharpe primario {sr:+.3f})")

    # Marginal-zone robustness check (only if any sample landed in [0.2, 0.4]).
    intentos = 2
    if marginal:
        intentos = 4  # 2 lookbacks x 2 samples (swap runs don't count)
        print("\n>>> Zona marginal disparada: chequeo de robustez (lookback 6m), "
              "intentos = 4, deflated Sharpe.")
        all_sr = []
        rob = {}
        for name, cols in (("A", SAMPLE_A), ("B", SAMPLE_B)):
            r6 = run_sample(name, cols, LOOKBACKS["robustness"])
            rob[name] = r6[PRIMARY_SWAP_BP]
            all_sr += [primary[name][PRIMARY_SWAP_BP], r6[PRIMARY_SWAP_BP]]
            print(f"    Muestra {name} lookback 6m: Sharpe neto = {r6[PRIMARY_SWAP_BP]:+.3f}")
        best = max(all_sr)
        haircut = _expected_max_sharpe_null(all_sr)
        deflated = best - haircut
        print(f"    mejor Sharpe = {best:+.3f} | haircut E[max|null] = {haircut:.3f} "
              f"| DEFLATED = {deflated:+.3f}")
        promote = deflated > SUCCESS
        print(f"    regla_decision: promueve sólo si deflated > {SUCCESS} → "
              f"{'PROMUEVE' if promote else 'PARKED'}")

    # Two-sample rule (post-2010 degradation).
    print("\n" + "=" * 72)
    if verdicts["A"] == "viable" and verdicts["B"] == "muerta":
        print("HALLAZGO: degradación post-2010 — A (con 2008) funciona, B (moderno) no.")
    print("Intentos genuinos:", intentos)
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
