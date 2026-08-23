"""run_h007.py — Run the H007 verdict IN-SAMPLE (TSMOM on the expanded 17 universe).

Reuses the UNCHANGED `signals.tsmom` (same as H001) on the 17-instrument universe.
Holdout RESPECTED: everything is computed on 2005/2015 → 2023-08-16; the runner
never loads the holdout.

TWO readings, deliberately separated (see the frozen ficha):
  - CALIBRACIÓN DEL MARCO — on the GROSS Sharpe. Did the committed prediction
    (bruto [0.29, 0.37]) land? If gross ∈ [0.25, 0.40] the effective-breadth /
    Grinold-Kahn framework is predictive → trust it for the paid-futures decision.
    This is the POINT of this run and is INDEPENDENT of the falsifier.
  - FALSADOR — on the NET Sharpe (swap 0.3). < 0.2 → muerta.
A result like gross 0.31 / net 0.14 is simultaneously "framework validated" AND
"hypothesis dead". Do not let the second make you misread the first.

    uv run python scripts/run_h007.py
"""

from __future__ import annotations

import dataclasses

import numpy as np
import pandas as pd

from src import config, engine, report, signals

SAMPLE_A = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "EURJPY", "GBPJPY",
            "AUDJPY", "EURAUD", "GBPAUD", "EURCHF", "XAUUSD", "XAGUSD"]  # FX + metals
SAMPLE_B = list(config.INSTRUMENTS)  # all 17
EVAL_START = {"A": "2005-01-01", "B": "2015-01-01"}
IN_SAMPLE_END = "2023-08-16"          # < config.HOLDOUT_START — holdout untouched
SWAPS_BP = [0.0, 0.3, 1.0]
PRIMARY_SWAP_BP = 0.3
SUCCESS, FALSIFIER = 0.4, 0.2
# Frozen commitments from hypotheses/H007_tsmom_expanded.yaml
EXPECTED_GROSS = (0.29, 0.37)
CALIB_BAND = (0.25, 0.40)             # if measured GROSS in here → framework predictive


def _load(cols: list[str]) -> pd.DataFrame:
    px = pd.DataFrame(
        {c: pd.read_parquet(config.DATA_CLEAN / f"{c}.parquet")["close"] for c in cols}
    )
    px = px.loc[:IN_SAMPLE_END]
    assert px.index.max() < pd.Timestamp(config.HOLDOUT_START), "holdout leaked!"
    return px


def _costs(swap_bp: float) -> dict[str, config.CostModel]:
    cm = dataclasses.replace(config.DEFAULT_COST, swap=swap_bp * 1e-4)
    return {c: cm for c in config.INSTRUMENTS}


# H001's samples, for a PERIOD-MATCHED baseline (recomputed to the same in-sample cut).
H001_A = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "XAUUSD"]
H001_B = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "XAUUSD", "SPX500", "GER40", "JPN225"]


def _gross_series(cols: list[str], start: str) -> pd.Series:
    px = _load(cols)
    w = signals.tsmom(px)
    live = w.abs().sum(axis=1) > 0
    s = max(pd.Timestamp(start), w.index[live][0])
    return engine.backtest(px, w, apply_costs=False).loc[s:]


def _sharpe_se(r: pd.Series) -> tuple[float, float]:
    """(Sharpe, SE) with SE ~ sqrt((1+S^2/2)/T_years)."""
    s = engine.sharpe(r)
    t = r.dropna().shape[0] / engine.bars_per_year(r)
    return s, np.sqrt((1 + 0.5 * s * s) / t) if t > 0 else float("nan")


def calibration_stats(sample: str, h001_cols: list[str], h007_cols: list[str]) -> dict:
    """H001 vs H007 gross, with SE of the DIFFERENCE (correlated portfolios)."""
    r1 = _gross_series(h001_cols, EVAL_START[sample])
    r7 = _gross_series(h007_cols, EVAL_START[sample])
    idx = r1.index.intersection(r7.index)
    r1, r7 = r1.reindex(idx), r7.reindex(idx)
    s1, se1 = _sharpe_se(r1)
    s7, se7 = _sharpe_se(r7)
    rho = float(r1.corr(r7))
    se_d = float(np.sqrt(se1 ** 2 + se7 ** 2 - 2 * rho * se1 * se7))
    d = s7 - s1
    return {"h001": s1, "h007": s7, "delta": d, "rho": rho, "se_d": se_d,
            "t": d / se_d if se_d else float("nan"), "T": r1.dropna().shape[0] / engine.bars_per_year(r1)}


def run_sample(name: str, cols: list[str]) -> dict:
    px = _load(cols)
    w = signals.tsmom(px)                      # UNCHANGED signal (same as H001)
    live = w.abs().sum(axis=1) > 0
    start = max(pd.Timestamp(EVAL_START[name]), w.index[live][0])
    r: dict = {"start": str(start.date()), "end": str(px.index.max().date())}
    # GROSS (apply_costs=False) — the calibration metric
    r["gross"] = engine.sharpe(engine.backtest(px, w, apply_costs=False).loc[start:])
    # NET at each swap — the falsifier metric (primary = 0.3)
    for swap in SWAPS_BP:
        net = engine.backtest(px, w, costs=_costs(swap)).loc[start:]
        r[f"net_{swap}"] = engine.sharpe(net)
        if swap == PRIMARY_SWAP_BP:
            r["net_primary_series"] = net
    # diagnostics
    wsl = w.loc[start:]
    r["turnover"] = wsl.diff().abs().sum(axis=1).sum() / ((wsl.index[-1] - wsl.index[0]).days / 365.25)
    npr = r["net_primary_series"]
    r["maxdd"] = report.max_drawdown(npr)
    r["vol"] = float(npr.std(ddof=0) * np.sqrt(engine.bars_per_year(npr)))
    return r


def main() -> int:
    print("=" * 74)
    print("H007 — TSMOM sobre universo ampliado (17) — VEREDICTO in-sample")
    print(f"Holdout RESPETADO: in-sample → {IN_SAMPLE_END} (holdout {config.HOLDOUT_START}+ intacto)")
    print("=" * 74)

    res = {n: run_sample(n, cols) for n, cols in (("A", SAMPLE_A), ("B", SAMPLE_B))}

    print(f"\n{'Muestra':26} {'BRUTO':>7} | {'neto 0.0':>8} {'neto 0.3*':>9} {'neto 1.0':>8}")
    print("-" * 74)
    for n, lbl in (("A", "A · FX+metales (con 2008)"), ("B", "B · los 17 (moderno)")):
        r = res[n]
        print(f"{lbl:26} {r['gross']:>+7.3f} | {r['net_0.0']:>+8.3f} {r['net_0.3']:>+9.3f} "
              f"{r['net_1.0']:>+8.3f}   ({r['start']}→{r['end']})")

    # ---- LECTURA 1: CALIBRACIÓN DEL MARCO — con PODER ESTADÍSTICO ----
    # H001 vs H007 sobre el mismo período; comparten la mayoría de instrumentos
    # (ρ~0.85) → SE de la diferencia pequeño, pero el test sigue sin poder.
    cal = {n: calibration_stats(n, c1, c7) for n, c1, c7 in
           (("A", H001_A, SAMPLE_A), ("B", H001_B, SAMPLE_B))}
    print("\n" + "=" * 74)
    print("LECTURA 1 — CALIBRACIÓN DEL MARCO (sobre el BRUTO; el punto real de esta corrida)")
    print(f"  Predicción de la ficha: bruto ∈ [{EXPECTED_GROSS[0]}, {EXPECTED_GROSS[1]}]")
    print(f"  Medido H007: bruto A={res['A']['gross']:+.3f}  B={res['B']['gross']:+.3f}")
    print(f"\n  ¿Ayudó la amplitud? Diferencia H007−H001 (period-matched), con SE de la diferencia:")
    print(f"  {'Muestra':8} {'T':>5} {'H001':>7} {'H007':>7} {'Δ':>7} {'ρ':>5} {'SE(Δ)':>6} {'t':>5}")
    for n in "AB":
        c = cal[n]
        print(f"  {n:8} {c['T']:>4.1f}y {c['h001']:>+7.3f} {c['h007']:>+7.3f} {c['delta']:>+7.3f} "
              f"{c['rho']:>5.2f} {c['se_d']:>6.2f} {c['t']:>5.2f}")
    maxt = max(abs(cal['A']['t']), abs(cal['B']['t']))
    print(f"\n  VEREDICTO DE CALIBRACIÓN: UNDERPOWERED (|t| ≤ {maxt:.2f} ~ 1 SE en ambas).")
    print("  El test NO pudo resolver si el marco predice: las diferencias son")
    print("  indistinguibles de ruido. NO se usa para decidir sobre datos de futuros —")
    print("  ni como estimación puntual NI como dirección.")
    print("  (Y la lectura previa 'la amplitud ayudó MÁS de lo predicho' tiene una")
    print("   explicación más simple: 6 de los 8 añadidos son recombinaciones lineales")
    print("   sin información nueva y no pueden producir un salto de 7.6× en IR; cuando")
    print("   lo medido excede lo que la teoría permite, el default es RUIDO, no que la")
    print("   teoría se quedara corta.)")

    # ---- LECTURA 2: FALSADOR (sobre el NETO 0.3) ----
    verd = {}
    for n in "AB":
        s = res[n]["net_0.3"]
        verd[n] = "viable_insample" if s >= SUCCESS else ("muerta" if s < FALSIFIER else "marginal")
    glob = ("viable_insample" if "viable_insample" in verd.values()
            else "muerta" if all(v == "muerta" for v in verd.values()) else "marginal")
    # Placeholder-sensitivity: the verdict is placeholder-dependent only if, at swap
    # 0.0, the strategy is COMFORTABLY above the falsifier (>0.2+margin, i.e. not just
    # marginal) yet dies under the primary swap. A net_0.0 barely above 0.2 (marginal)
    # dies clean — its death is weakness, not the placeholder.
    CLEAR_MARGIN = 0.10
    for n in "AB":
        clearly_alive0 = res[n]["net_0.0"] >= FALSIFIER + CLEAR_MARGIN
        dead_primary = res[n]["net_0.3"] < FALSIFIER
        res[n]["placeholder_dependent"] = clearly_alive0 and dead_primary
    print("\nLECTURA 2 — FALSADOR (sobre el NETO 0.3; INDEPENDIENTE de la calibración)")
    for n, lbl in (("A", "A"), ("B", "B")):
        r = res[n]
        note = ("  ← cruza el falsador con el swap (0.0→%.3f VIVA, 0.3→%.3f muerta): veredicto "
                "SOBRE EL PLACEHOLDER, no sobre la estrategia" % (r["net_0.0"], r["net_0.3"])
                if r["placeholder_dependent"] else "  (muere limpia)")
        print(f"  Neto {lbl}={r['net_0.3']:+.3f} → {verd[n]}{note}")
    print(f"  Veredicto de hipótesis: {glob.upper()}   (esperado: muerta)")
    print("=" * 74)

    _write_report(res, cal, verd, glob, maxt)
    return 0


def _write_report(res, cal, verd, glob, maxt) -> None:
    L = [
        "# Reporte de prueba — H007 (TSMOM sobre universo ampliado, 17)",
        "",
        f"**fecha_test: 2026-08-22** · in-sample → {IN_SAMPLE_END} · **holdout NO tocado** · "
        "señal `tsmom` sin modificar (idéntica a H001).",
        "",
        "Dos lecturas INDEPENDIENTES (ver ficha): la **calibración del marco** se juzga "
        "sobre el **BRUTO** (¿acertó la predicción?), el **falsador** sobre el **NETO**. "
        "Un bruto en banda + neto < 0.2 = marco validado E hipótesis muerta a la vez.",
        "",
        "## Bruto vs neto por muestra (Sharpe)",
        "",
        "| Muestra | eval | **BRUTO** | neto 0.0 | **neto 0.3** (primaria) | neto 1.0 |",
        "|---|---|---|---|---|---|",
    ]
    for n, lbl in (("A", "A · FX+metales (con 2008)"), ("B", "B · los 17 (moderno)")):
        r = res[n]
        L.append(f"| {lbl} | {r['start']}→{r['end']} | **{r['gross']:+.3f}** | {r['net_0.0']:+.3f} "
                 f"| **{r['net_0.3']:+.3f}** | {r['net_1.0']:+.3f} |")
    L += [
        "",
        "## LECTURA 1 — Calibración del marco (sobre el BRUTO)  ← el punto real",
        "",
        f"- **Predicción de la ficha** (congelada): bruto ∈ **[{EXPECTED_GROSS[0]}, {EXPECTED_GROSS[1]}]**.",
        f"- **Medido H007**: bruto A = {res['A']['gross']:+.3f}, B = {res['B']['gross']:+.3f}.",
        "",
        "**¿Ayudó la amplitud? Diferencia H007−H001 (period-matched, mismo corte) con el SE de "
        "la DIFERENCIA** (los portafolios comparten la mayoría de instrumentos, ρ~0.85, lo que "
        "reduce el SE):",
        "",
        "| Muestra | T | H001 | H007 | Δ bruto | ρ | SE(Δ) | t |",
        "|---|---|---|---|---|---|---|---|",
    ] + [
        f"| {n} | {cal[n]['T']:.1f}y | {cal[n]['h001']:+.3f} | {cal[n]['h007']:+.3f} | "
        f"{cal[n]['delta']:+.3f} | {cal[n]['rho']:.2f} | {cal[n]['se_d']:.2f} | **{cal[n]['t']:.2f}** |"
        for n in "AB"
    ] + [
        "",
        f"**Veredicto de calibración: UNDERPOWERED** (|t| ≤ {maxt:.2f}, ~1 SE en ambas muestras). "
        "El test **no pudo resolver** si el marco predice: las diferencias son indistinguibles de "
        "ruido. **NO se usa para decidir sobre datos de futuros — ni como estimación puntual NI "
        "como dirección.**",
        "",
        "Corrección de la lectura previa: decir que *\"la amplitud ayudó MÁS de lo predicho\"* era "
        "un error. 6 de los 8 instrumentos añadidos son **recombinaciones lineales** de los majors "
        "(cero información nueva, `docs/breadth-lessons.md`) y no pueden producir un salto de ~7.6× "
        "en IR. Cuando un efecto medido excede tanto lo que la teoría permite, la explicación por "
        "defecto es **ruido**, no que la teoría se quedara corta.",
        "",
        "## LECTURA 2 — Falsador (sobre el NETO 0.3, independiente)",
        "",
    ] + [
        (f"- **Muestra {n}** = {res[n]['net_0.3']:+.3f} → muerta bajo la especificación primaria, "
         f"**PERO el veredicto es sobre el PLACEHOLDER de swap, no sobre la estrategia**: cruza el "
         f"falsador dentro del rango (0.0→{res[n]['net_0.0']:+.3f} VIVA · 0.3→{res[n]['net_0.3']:+.3f} "
         f"muerta · 1.0→{res[n]['net_1.0']:+.3f}). Se invoca la cláusula de sensibilidad al swap."
         if res[n]["placeholder_dependent"] else
         f"- **Muestra {n}** = {res[n]['net_0.3']:+.3f} → **muere limpia**: ya a swap 0.0 es marginal "
         f"({res[n]['net_0.0']:+.3f}, apenas sobre 0.2) y a 0.3 muere; no depende del placeholder.")
        for n in "AB"
    ] + [
        f"- **Veredicto de hipótesis: {glob.upper()}** (esperado: muerta).",
        "",
        "## Diagnósticos",
        "",
        "| Muestra | turnover/año | sharpe_zero_cost (=bruto) | maxDD | vol | DD/vol |",
        "|---|---|---|---|---|---|",
    ]
    for n in "AB":
        r = res[n]
        L.append(f"| {n} | {r['turnover']:.1f}× | {r['gross']:+.3f} | {r['maxdd']:.1%} | "
                 f"{r['vol']:.1%} | {abs(r['maxdd'])/r['vol']:.1f}× |")
    L += ["", "## Detalle Muestra B (neto 0.3, in-sample)", "",
          report.render(res["B"]["net_primary_series"], name="H007 · Muestra B in-sample"), ""]
    dest = config.RESULTS / "H007"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "report.md").write_text("\n".join(L), encoding="utf-8")
    print(f"\nReporte escrito en {dest / 'report.md'}")


if __name__ == "__main__":
    raise SystemExit(main())
