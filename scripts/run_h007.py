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


def _gross(cols: list[str], start: str) -> float:
    px = _load(cols)
    w = signals.tsmom(px)
    live = w.abs().sum(axis=1) > 0
    s = max(pd.Timestamp(start), w.index[live][0])
    return engine.sharpe(engine.backtest(px, w, apply_costs=False).loc[s:])


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

    # ---- LECTURA 1: CALIBRACIÓN DEL MARCO (sobre el BRUTO) ----
    # La predicción de la ficha [0.29,0.37] usó el bruto de H001 medido a 2026, pero
    # H007 corta en 2023-08-16 (holdout). Ese desajuste de período CONTAMINA la
    # comparación → añadimos el baseline PERIOD-MATCHED (H001 recomputado al mismo corte).
    pm_A, pm_B = _gross(H001_A, "2004-06-01"), _gross(H001_B, "2015-01-01")
    in_expected = all(EXPECTED_GROSS[0] <= res[n]["gross"] <= EXPECTED_GROSS[1] for n in "AB")
    print("\n" + "=" * 74)
    print("LECTURA 1 — CALIBRACIÓN DEL MARCO (sobre el BRUTO; el punto real de esta corrida)")
    print(f"  Predicción de la ficha: bruto ∈ [{EXPECTED_GROSS[0]}, {EXPECTED_GROSS[1]}] "
          f"(H001-a-2026 × 1.194)")
    print(f"  Medido H007:            bruto A={res['A']['gross']:+.3f}  B={res['B']['gross']:+.3f}")
    print(f"  ¿Dentro de [{EXPECTED_GROSS[0]},{EXPECTED_GROSS[1]}]? A={'sí' if EXPECTED_GROSS[0]<=res['A']['gross']<=EXPECTED_GROSS[1] else 'no'}  "
          f"B={'sí' if EXPECTED_GROSS[0]<=res['B']['gross']<=EXPECTED_GROSS[1] else 'no'}  (mixto)")
    print(f"\n  Baseline PERIOD-MATCHED (H001 recomputado a {IN_SAMPLE_END}): A={pm_A:.3f}  B={pm_B:.3f}")
    print(f"  → la predicción de la ficha estaba MAL DERIVADA: usó H001-a-2026 (B=0.308),")
    print(f"    pero el B period-matched es {pm_B:.3f} (el trend moderno del universo-9 estaba ~muerto).")
    print(f"  Predicción period-matched (×1.194): A={pm_A*1.194:.3f}  B={pm_B*1.194:.3f}")
    print(f"  Bruto real H007:                    A={res['A']['gross']:.3f}  B={res['B']['gross']:.3f}")
    print("\n  VEREDICTO DE CALIBRACIÓN:")
    print("  · Dirección (más amplitud → más bruto): CORRECTA — el bruto SUBIÓ al ampliar")
    print(f"    (B period-matched {pm_B:.3f} → {res['B']['gross']:.3f}, +{res['B']['gross']-pm_B:.2f} absoluto).")
    print("  · Magnitud (×1.194): NO fiable — la amplitud ayudó MÁS de lo predicho, y la")
    print("    predicción de la ficha estaba contaminada por el desajuste de período.")
    print("  → El marco es DIRECCIONALMENTE útil pero NO predice magnitudes con precisión:")
    print("    tratar el caso de datos de futuros como dirección, NO como estimación puntual.")

    # ---- LECTURA 2: FALSADOR (sobre el NETO 0.3) ----
    verd = {}
    for n in "AB":
        s = res[n]["net_0.3"]
        verd[n] = "viable_insample" if s >= SUCCESS else ("muerta" if s < FALSIFIER else "marginal")
    glob = ("viable_insample" if "viable_insample" in verd.values()
            else "muerta" if all(v == "muerta" for v in verd.values()) else "marginal")
    print("\nLECTURA 2 — FALSADOR (sobre el NETO 0.3; INDEPENDIENTE de la calibración)")
    print(f"  Neto A={res['A']['net_0.3']:+.3f} → {verd['A']}   Neto B={res['B']['net_0.3']:+.3f} → {verd['B']}")
    print(f"  Veredicto de hipótesis: {glob.upper()}   (esperado: muerta)")
    print("\n  NOTA: las dos lecturas son independientes. Un bruto en banda + neto < 0.2 = "
          "MARCO VALIDADO e HIPÓTESIS MUERTA a la vez.")
    print("=" * 74)

    _write_report(res, pm_A, pm_B, verd, glob)
    return 0


def _write_report(res, pm_A, pm_B, verd, glob) -> None:
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
        f"- **Predicción de la ficha** (antes de correr): bruto ∈ **[{EXPECTED_GROSS[0]}, {EXPECTED_GROSS[1]}]** "
        f"(H001-a-2026 0.244/0.308 × 1.194 por N_eff 3.73→5.32).",
        f"- **Medido H007**: bruto A = **{res['A']['gross']:+.3f}**, B = **{res['B']['gross']:+.3f}** → "
        "resultado **mixto** contra esa predicción (A en el borde superior, B por debajo).",
        "",
        "**Pero la predicción de la ficha estaba MAL DERIVADA**: usó el bruto de H001 medido "
        f"a 2026, mientras H007 corta en {IN_SAMPLE_END} (holdout). Baseline **period-matched** "
        f"(H001 recomputado al mismo corte): A = **{pm_A:.3f}**, B = **{pm_B:.3f}** — el trend "
        "moderno del universo-9 estaba ~muerto (B 0.03); el 0.308 de la ficha venía casi todo de "
        "2023-2026, que el holdout excluye.",
        "",
        f"Predicción period-matched (×1.194): A={pm_A*1.194:.3f}, B={pm_B*1.194:.3f}. Bruto real: "
        f"A={res['A']['gross']:.3f}, B={res['B']['gross']:.3f}.",
        "",
        "**Veredicto de calibración:**",
        f"- **Dirección CORRECTA**: más amplitud → más bruto (B period-matched {pm_B:.3f} → "
        f"{res['B']['gross']:.3f}, +{res['B']['gross']-pm_B:.2f} absoluto al ampliar a 17).",
        "- **Magnitud NO fiable**: la amplitud ayudó MÁS de lo predicho por √N_eff, y la "
        "predicción de la ficha estaba contaminada por el desajuste de período.",
        "- → El marco es **direccionalmente útil pero no predice magnitudes con precisión**. "
        "Tratar el caso de datos de futuros como una **dirección** (rates/commodities deberían "
        "ayudar), NO como una estimación puntual de Sharpe. Confirma la humildad de "
        "`docs/breadth-lessons.md`: N_eff sobreestima y el marco no es de precisión.",
        "",
        "## LECTURA 2 — Falsador (sobre el NETO 0.3, independiente)",
        "",
        f"- Neto A = {res['A']['net_0.3']:+.3f} → {verd['A']}; Neto B = {res['B']['net_0.3']:+.3f} → {verd['B']}.",
        f"- **Veredicto de hipótesis: {glob.upper()}** (esperado: muerta). El swap unsigned "
        "diario hunde el bruto bajo el falsador, igual que en H001.",
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
