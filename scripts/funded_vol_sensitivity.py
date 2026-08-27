"""funded_vol_sensitivity.py — ¿muerde la barrera a vol alta? ¿mejora el valor esperado?

Motivación: `funded_sharpe_requirement` halló P(quemar)≈0 → el cuello es PASAR, no sobrevivir.
Eso pone en duda la restricción de vol al 8% (§2.1 del documento maestro). Barrido de vol para
los Sharpe REALMENTE alcanzables {0.3, 0.37, 0.5}, con los tres CAVEATS que empeoran el resultado
LEVANTADOS:

 (a) SUPERVIVENCIA ACUMULATIVA, no independiente: el modelo de fase fondeada anterior trata cada
     ciclo como independiente (p_survive^N, optimista). Aquí se simula el CAMINO CONTINUO de N×21
     días y se comprueba el drawdown estático de -10% acumulado desde el inicio → captura los
     drawdowns que se ACUMULAN. Se reporta también el independiente como cota optimista.
 (b) RETORNOS REALES, no normales: además del sintético normal, se bootstrapea la FORMA de una
     cartera CFD real (riesgo-igual de los 17, curtosis en exceso ~3.2, skew −0.27),
     estandarizada al objetivo (Sharpe, vol) — inyecta colas gordas y autocorrelación reales.
 (c) LÍMITE DIARIO INTRADÍA: en la realidad el −5% diario se evalúa intradía; aquí sobre cierres.
     Se acota con un factor intradía sobre la magnitud del movimiento diario (1.0 cierres / 1.8 proxy).

Todos empujan el resultado hacia PEOR. Si aun así la vol alta mejora el valor esperado, es real.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src import challenge as ch
from src import config
from scripts.funded_sharpe_requirement import swap_drag_daily, CHALLENGE_FEE, SPLIT, ACCOUNT, TRADING_DAYS

SHARPES = [0.3, 0.37, 0.5]
VOLS = [0.08, 0.12, 0.15, 0.20, 0.25]
MULT = 1.0                      # BROKER_MARGIN_MULT base (la sensibilidad 1.5 ya está en el otro doc)
SCALING = [50_000, 150_000, 300_000]
N_BASE = 4000
CYCLE = config.DEFAULT_FIRM_RULES.payout_interval_days   # 21


def _real_shape() -> np.ndarray:
    """Serie diaria de una cartera CFD real (riesgo-igual de los 17): forma con colas reales."""
    rs = {c: pd.read_parquet(config.DATA_CLEAN / f"{c}.parquet")["close"].pct_change()
          for c in config.INSTRUMENTS}
    df = pd.DataFrame(rs).loc["2014-01-01":].dropna(how="any")
    iv = 1.0 / df.std()
    port = (df * iv).sum(axis=1) / iv.sum()
    z = port.to_numpy()
    return (z - z.mean()) / z.std(ddof=0)   # forma estandarizada (media 0, desv 1)


_REAL_Z = None


def base_series(sharpe: float, vol: float, mult: float, source: str, seed: int) -> np.ndarray:
    """Serie base NETA con momentos objetivo. source='normal' | 'real' (forma CFD real)."""
    global _REAL_Z
    sig_d = vol / np.sqrt(TRADING_DAYS)
    mu_d = sharpe * vol / TRADING_DAYS - swap_drag_daily(mult)
    if source == "real":
        if _REAL_Z is None:
            _REAL_Z = _real_shape()
        z = _REAL_Z
    else:
        rng = np.random.default_rng(seed)
        z = rng.normal(0.0, 1.0, N_BASE)
        z = (z - z.mean()) / z.std(ddof=0)
    return mu_d + sig_d * z


def funded_survive_accum(net: np.ndarray, n_cycles: int, *, intraday_mult: float, seed: int) -> float:
    """P(sobrevivir) sobre el CAMINO CONTINUO de n_cycles×21 días (drawdown estático −10% acumulado
    desde el inicio; límite diario −5% con inflación intradía). ACUMULATIVA, no independiente."""
    rules, params = config.DEFAULT_FIRM_RULES, config.DEFAULT_SIM_PARAMS
    horizon = n_cycles * CYCLE
    rng = np.random.default_rng(seed)
    paths = ch.block_bootstrap(net, n_paths=params.n_bootstraps, horizon=horizon,
                               block_size=params.block_size, rng=rng)
    level = np.cumsum(paths, axis=1)
    dd_hit = (level <= -rules.max_drawdown).any(axis=1)                     # drawdown acumulado
    daily_hit = (paths * intraday_mult <= -rules.daily_loss_limit).any(axis=1)  # límite diario intradía
    return float((~(dd_hit | daily_hit)).mean())


def run_cell(sharpe: float, vol: float, source: str, intraday_mult: float, seed: int) -> dict:
    net = base_series(sharpe, vol, MULT, source, seed)
    res = ch.simulate_challenge(net, leverage=1.0, with_leverage_curve=False)
    # supervivencia ACUMULATIVA a N ciclos (caveat a), con inflación intradía (caveat c)
    p_surv = {n: funded_survive_accum(net, n, intraday_mult=intraday_mult, seed=seed + n)
              for n in (4, 8, 12)}
    net_annual = sharpe * vol - swap_drag_daily(MULT) * TRADING_DAYS
    p_pass = res.p_pass_conditional
    p_exito = p_pass * p_surv[12]
    payout_year = SPLIT * net_annual * ACCOUNT
    # valor esperado NETO de cuotas por año (decisión): payout×P(sobrevivir año) − cuotas de fondeo/refondeo
    p_cycle = p_surv[12] ** (1 / 12) if p_surv[12] > 0 else 0.0
    fees_year = (CHALLENGE_FEE / max(p_pass, 1e-6)) * (1 + 12 * (1 - p_cycle))
    ev_year_50k = payout_year * p_surv[12] - fees_year
    ev_year_300k = SPLIT * net_annual * 300_000 * p_surv[12] - fees_year
    return {"sharpe": sharpe, "vol": vol, "source": source, "intraday": intraday_mult,
            "p_pass": p_pass, "days": res.expected_days_to_pass, "insuf": res.insufficient_horizon,
            "p_burn4": 1 - p_surv[4], "p_burn8": 1 - p_surv[8], "p_burn12": 1 - p_surv[12],
            "net_annual": net_annual, "payout_year": payout_year, "p_exito": p_exito,
            "ev_year_50k": ev_year_50k, "ev_year_300k": ev_year_300k}


def _fmt_days(r):
    return "nan" if (r["insuf"] or not np.isfinite(r["days"])) else f"{r['days']:.0f}"


def main():
    seed0 = config.DEFAULT_SIM_PARAMS.seed

    print("=== D1. Barrido de vol (sintético normal, mult 1.0, intradía 1.0) ===")
    print(f"{'S':>5} {'vol':>5} {'Ppass':>6} {'días':>6} {'burn4':>6} {'burn8':>6} {'burn12':>7} "
          f"{'ret%':>6} {'Péxito':>7} {'EV/año 300k$':>12}")
    rows = []
    for si, s in enumerate(SHARPES):
        for vi, v in enumerate(VOLS):
            r = run_cell(s, v, "normal", 1.0, seed0 + 100 * si + vi)
            rows.append(r)
            print(f"{s:>5} {v*100:>4.0f}% {r['p_pass']:>6.2f} {_fmt_days(r):>6} {r['p_burn4']:>6.2f} "
                  f"{r['p_burn8']:>6.2f} {r['p_burn12']:>7.2f} {r['net_annual']*100:>5.1f} "
                  f"{r['p_exito']:>7.2f} {r['ev_year_300k']:>12.0f}")

    print("\n=== D2. ¿A qué vol EMPIEZA a morder la barrera? (P(burn 12), normal vs REAL, intradía 1.0 y 1.8) ===")
    print(f"{'S':>5} {'vol':>5} {'burn12 normal':>14} {'burn12 real':>12} {'burn12 real+intra1.8':>20}")
    for s in [0.37]:   # el Sharpe alcanzable focal
        for vi, v in enumerate(VOLS):
            rn = run_cell(s, v, "normal", 1.0, seed0 + vi)
            rr = run_cell(s, v, "real", 1.0, seed0 + 50 + vi)
            ri = run_cell(s, v, "real", 1.8, seed0 + 90 + vi)
            print(f"{s:>5} {v*100:>4.0f}% {rn['p_burn12']:>14.2f} {rr['p_burn12']:>12.2f} {ri['p_burn12']:>20.2f}")

    print("\n=== D3. Valor esperado neto de cuotas por AÑO — ¿mejora con vol? (Sharpe 0.37) ===")
    print(f"{'vol':>5} {'source':>7} {'intra':>6} {'ret%':>6} {'payout/año$':>11} {'Péxito':>7} "
          f"{'EV/año 50k$':>12} {'EV/año 300k$':>13}")
    for v in VOLS:
        for source, intra in [("normal", 1.0), ("real", 1.0), ("real", 1.8)]:
            r = run_cell(0.37, v, source, intra, seed0 + int(v * 1000) + int(intra * 10))
            print(f"{v*100:>4.0f}% {source:>7} {intra:>6.1f} {r['net_annual']*100:>5.1f} "
                  f"{r['payout_year']:>11.0f} {r['p_exito']:>7.2f} {r['ev_year_50k']:>12.0f} {r['ev_year_300k']:>13.0f}")

    # D4 respuesta: mejor EV/año a Sharpe 0.37 bajo el caso PESIMISTA (real + intradía 1.8)
    pes = [run_cell(0.37, v, "real", 1.8, seed0 + 700 + i) for i, v in enumerate(VOLS)]
    best = max(pes, key=lambda r: r["ev_year_300k"])
    base8 = next(r for r in pes if abs(r["vol"] - 0.08) < 1e-9)
    print("\n=== D4. LA RESPUESTA ===")
    print(f"  Bajo el caso PESIMISTA (real+intradía1.8), Sharpe 0.37:")
    print(f"  EV/año (300k) por vol: " + " · ".join(f"{r['vol']*100:.0f}%→${r['ev_year_300k']:.0f}" for r in pes))
    print(f"  mejor vol = {best['vol']*100:.0f}% (EV ${best['ev_year_300k']:.0f}) vs 8% (${base8['ev_year_300k']:.0f}); "
          f"burn12 a esa vol = {best['p_burn12']:.2f}")

    # D5 — decisión Norgate: N_eff necesario para cerrar el hueco por AMPLITUD
    print("\n=== D5. Decisión Norgate — N_eff para cerrar el hueco 0.37→target (Sharpe ∝ √N_eff) ===")
    neff_src = 8.15   # ancla: universo de futuros (el más ancho accesible), donde trend ~0.37
    for tgt in (0.50, 0.80):
        need = neff_src * (tgt / 0.37) ** 2
        print(f"  0.37 → {tgt}: N_eff necesario ≈ {need:.0f}  (desde {neff_src} de futuros)")
    print("  Expectativa comprometida de amplitud de futuros: 9-12 (futures_case.md); medido 8.15.")
    print("  → los $50/mes compran N_eff ~8, NO 15 ni 38. NO cierra el hueco. NO se contrata.")


if __name__ == "__main__":
    main()
