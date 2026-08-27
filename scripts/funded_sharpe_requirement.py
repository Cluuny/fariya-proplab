"""funded_sharpe_requirement.py — ¿qué Sharpe hace falta para pasar, ganar y sobrevivir?

Aritmética sobre `src/challenge.py` (el simulador de barrera, semana 4), aplicado por primera vez
a la pregunta del CICLO COMPLETO de fondeo. NO requiere datos nuevos ni suscripción.

Modelo (documentado, honesto):
- El Sharpe barrido es BRUTO (para contrastar directo con lo medido: H002 0.495, H007-A 0.370,
  industria ~0.32). El NETO que mueve la cuenta = bruto − drag de swap.
- SWAP DIRECCIONAL (no el placeholder unsigned): en un libro long/short DIVERSIFICADO el carry
  con signo ~se cancela (hallazgo del programa), así que el drag residual es el MARGEN
  unidireccional del broker: _MARGIN_FX·BROKER_MARGIN_MULT·(365/261) ≈ 0.42 bp/d (mult 1.0) /
  0.63 (mult 1.5), sobre exposición ~1. (Un libro con carry NETO —como H002— lo desplazaría por
  el carry histórico con signo; para la CURVA de requisito usamos el libro balanceado.)
- Retornos sintéticos ~ N(S·V/252 − c, V/√252), bootstrapeados en bloques por challenge.py.
- GUARDS respetados: p_unresolved>5% → días=nan (horizonte insuficiente); optimal_leverage=None
  (objetivo no definido); leverage fijo=1.0 (barremos VOL, no leverage).

Economía ($50k, split 90%, escalado $50k→$150k→$300k por consistencia; cuota de challenge
representativa $300 para 50k). Assumptions marcadas.
"""

from __future__ import annotations

import numpy as np

from src import config
from src import challenge as ch

SHARPES = [0.0, 0.2, 0.3, 0.5, 0.8, 1.0, 1.5]
VOLS = [0.06, 0.08, 0.10]
MARGIN_MULTS = [1.0, 1.5]
ACCOUNT = 50_000
SPLIT = 0.90
CHALLENGE_FEE = 300.0            # cuota representativa de un challenge de $50k (FTMO ~€345)
SCALING = [50_000, 150_000, 300_000]   # escalado interno por consistencia
N_BASE = 4000                   # longitud de la serie sintética base
TRADING_DAYS = 252


def swap_drag_daily(mult: float) -> float:
    """Drag de swap NETO/día en un libro balanceado = margen unidireccional (carry ~0)."""
    return config._MARGIN_FX * mult * config.TRADING_DAY_SWAP_FACTOR   # ≈0.000042 (1.0)/0.000063 (1.5)


def synth_returns(sharpe_gross: float, vol: float, mult: float, seed: int) -> np.ndarray:
    """Serie diaria NETA sintética con momentos EXACTOS: bruto de Sharpe S y vol V, menos el drag.

    Se ESTANDARIZA la muestra (resta media/divide desv. realizadas, reescala al objetivo) para
    que la serie base tenga exactamente (mu_d, sig_d) — sin esto, el Sharpe REALIZADO de 4000
    draws tiene SE≈0.25 y ensucia el barrido (no-monotonicidad espuria). El bootstrap de bloques
    de challenge.py añade la varianza de camino sobre esta base limpia."""
    rng = np.random.default_rng(seed)
    sig_d = vol / np.sqrt(TRADING_DAYS)
    mu_d = sharpe_gross * vol / TRADING_DAYS - swap_drag_daily(mult)
    z = rng.normal(0.0, 1.0, N_BASE)
    z = (z - z.mean()) / z.std(ddof=0)          # momentos exactos: media 0, desv 1
    return mu_d + sig_d * z


def run_cell(sharpe: float, vol: float, mult: float, seed: int) -> dict:
    net = synth_returns(sharpe, vol, mult, seed)
    res = ch.simulate_challenge(net, leverage=1.0, with_leverage_curve=False)
    # supervivencia por ciclo de payout (para P(quemar antes de N) y P(sobrevivir 12))
    rng = np.random.default_rng(seed + 1)
    p_surv = ch._funded_phase(net, config.DEFAULT_FIRM_RULES, config.DEFAULT_SIM_PARAMS, rng)
    net_annual = sharpe * vol - swap_drag_daily(mult) * TRADING_DAYS   # retorno anual NETO esperado
    p_pass_both = res.p_pass_conditional                              # decisión, condicional a absorción
    p_exito = p_pass_both * p_surv ** 12
    payout_year = SPLIT * net_annual * ACCOUNT
    return {
        "sharpe": sharpe, "vol": vol, "mult": mult,
        "p1": res.p_phase1, "p2": res.p_phase2, "p_cond": p_pass_both,
        "days": res.expected_days_to_pass, "insuf": res.insufficient_horizon,
        "p_surv": p_surv,
        "p_burn4": 1 - p_surv ** 4, "p_burn8": 1 - p_surv ** 8, "p_burn12": 1 - p_surv ** 12,
        "net_annual": net_annual, "payout_year": payout_year, "p_exito": p_exito,
    }


def min_sharpe_for(rows: list[dict], vol: float, mult: float, thr: float) -> float | None:
    cand = [r for r in rows if abs(r["vol"] - vol) < 1e-9 and r["mult"] == mult and r["p_exito"] >= thr]
    return min((r["sharpe"] for r in cand), default=None)


def main():
    rows = []
    seed = config.DEFAULT_SIM_PARAMS.seed
    for i, mult in enumerate(MARGIN_MULTS):
        for j, vol in enumerate(VOLS):
            for k, s in enumerate(SHARPES):
                rows.append(run_cell(s, vol, mult, seed + 1000 * i + 100 * j + k))

    # D1
    print("=== D1. P(pasar)/P(quemar)/P(éxito) por Sharpe y vol (mult 1.0) ===")
    print(f"{'S':>4} {'vol':>4} {'P1':>6} {'P2':>6} {'Pcond':>6} {'días':>6} "
          f"{'Pburn4':>7} {'Pburn8':>7} {'Pburn12':>7} {'ret%':>6} {'payout$':>8} {'Péxito':>7}")
    for r in rows:
        if r["mult"] != 1.0:
            continue
        d = "nan" if (r["insuf"] or not np.isfinite(r["days"])) else f"{r['days']:.0f}"
        print(f"{r['sharpe']:>4} {r['vol']*100:>3.0f}% {r['p1']:>6.2f} {r['p2']:>6.2f} "
              f"{r['p_cond']:>6.2f} {d:>6} {r['p_burn4']:>7.2f} {r['p_burn8']:>7.2f} "
              f"{r['p_burn12']:>7.2f} {r['net_annual']*100:>5.1f} {r['payout_year']:>8.0f} {r['p_exito']:>7.2f}")

    print("\n=== D1b. sensibilidad BROKER_MARGIN_MULT 1.5 (vol 8%) ===")
    for r in rows:
        if r["mult"] == 1.5 and abs(r["vol"] - 0.08) < 1e-9:
            print(f"  S={r['sharpe']:>4}  Pcond {r['p_cond']:.2f}  Pburn12 {r['p_burn12']:.2f}  "
                  f"ret {r['net_annual']*100:.1f}%  Péxito {r['p_exito']:.2f}")

    # D2
    print("\n=== D2. Sharpe mínimo (BRUTO) para P(éxito) ≥ umbral ===")
    for vol in VOLS:
        for mult in MARGIN_MULTS:
            line = f"  vol {vol*100:.0f}%  mult {mult}:  "
            for thr in (0.50, 0.70, 0.80):
                m = min_sharpe_for(rows, vol, mult, thr)
                line += f"P≥{int(thr*100)}%→{m if m is not None else '>1.5'}   "
            print(line)

    # D3 — aritmética del dinero (vol 8%, mult 1.0, escalado)
    print("\n=== D3. Aritmética del dinero (vol 8%, mult 1.0, split 90%) ===")
    print(f"{'S':>4} {'ret%':>6} {'pay/mo 50k':>11} {'pay/mo 150k':>12} {'pay/mo 300k':>12} "
          f"{'#acc $1k/mo':>11} {'#acc $2.5k/mo':>13} {'fees/año$':>10}")
    for r in rows:
        if r["mult"] != 1.0 or abs(r["vol"] - 0.08) > 1e-9:
            continue
        pm = {sz: SPLIT * r["net_annual"] * sz / 12 for sz in SCALING}
        pm_best = pm[SCALING[-1]]   # con la cuenta escalada al máximo
        n_1k = ("∞" if pm_best <= 0 else f"{np.ceil(1000/pm_best):.0f}")
        n_25k = ("∞" if pm_best <= 0 else f"{np.ceil(2500/pm_best):.0f}")
        # cuotas/año ≈ fee × (1/Pcond) para fondearse + reintentos por quema (aprox, marcado)
        fees = (CHALLENGE_FEE / max(r["p_cond"], 1e-6)) * (1 + 12 * (1 - r["p_surv"])) if r["p_cond"] > 0 else float("inf")
        print(f"{r['sharpe']:>4} {r['net_annual']*100:>5.1f} {pm[50000]:>11.0f} {pm[150000]:>12.0f} "
              f"{pm[300000]:>12.0f} {n_1k:>11} {n_25k:>13} {fees:>10.0f}")

    # D5 — contraste
    print("\n=== D5. Contraste vs lo MEDIDO (bruto) ===")
    print("  Alcanzable (bruto): H002 0.495 · H007-A 0.370 · industria CTA ~0.32")
    m50 = min_sharpe_for(rows, 0.08, 1.0, 0.50)
    m70 = min_sharpe_for(rows, 0.08, 1.0, 0.70)
    m80 = min_sharpe_for(rows, 0.08, 1.0, 0.80)
    print(f"  Requerido (vol 8%, mult 1.0): P(éxito)≥50% → {m50} · ≥70% → {m70} · ≥80% → {m80}")


if __name__ == "__main__":
    main()
