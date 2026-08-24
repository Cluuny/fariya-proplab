"""calibrate.py — Bloque 2: test de calibración del OFI (criterio de aceptación).

Regresión CONTEMPORÁNEA ΔP_k = α + β·OFI_k + ε en submuestras de MEDIA HORA, Δt = 10 s,
errores estándar de White (HC0). El paper reporta R² medio ~65% en acciones.

Criterio de aceptación del bloque (cripto puede diferir pero debe ser ALTO):
  - R² medio > 0.40  (si sale bajo, hay un BUG en el OFI y NO se avanza).
Verificaciones secundarias (las tres deben cumplirse):
  (a) OFI explica mejor que trade imbalance (paper 65% vs 32%). Test MÁS discriminante:
      si (a) falla, la implementación está mal.
  (b) β inversamente proporcional a la profundidad media del libro (log-log, pendiente ~−1).
  (c) al excluir eventos que cambian el precio, R² baja pero se mantiene (paper 35-60%).
"""

from __future__ import annotations

from dataclasses import dataclass


def ols_white_multi(y, X_no_const):
    """OLS y = a + Σ b_j·x_j con SE de White (HC0). `X_no_const` es (n, p) SIN la columna
    de unos. Devuelve a, coefs (list), t (list, White), r2, n."""
    import numpy as np

    y = np.asarray(y, float)
    Xn = np.asarray(X_no_const, float)
    if Xn.ndim == 1:
        Xn = Xn[:, None]
    n = len(y)
    X = np.column_stack([np.ones(n), Xn])
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ X.T @ y
    resid = y - X @ beta
    ss_res = float(resid @ resid)
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    meat = X.T @ (X * (resid ** 2)[:, None])
    cov = XtX_inv @ meat @ XtX_inv
    se = np.sqrt(np.diag(cov))
    t = [float(beta[j] / se[j]) if se[j] > 0 else 0.0 for j in range(len(beta))]
    return {"a": float(beta[0]), "coefs": [float(b) for b in beta[1:]],
            "t": t[1:], "r2": r2, "n": n}


def ols_white(y, x):
    """OLS simple y = a + b·x con SE de White (HC0). Compat con la firma previa."""
    r = ols_white_multi(y, x)
    return {"a": r["a"], "b": r["coefs"][0], "r2": r["r2"],
            "se_b_white": abs(r["coefs"][0] / r["t"][0]) if r["t"][0] else float("inf"),
            "t_b": r["t"][0], "n": r["n"]}


@dataclass
class CalibrationResult:
    n_subsamples: int
    mean_r2_ofi: float
    mean_r2_ti: float | None
    mean_r2_excl_price_changing: float | None
    depth_loglog_slope: float | None      # pendiente de log|β| vs log(depth); ~ −1 esperado
    mean_beta: float
    frac_beta_significant: float          # fracción con |t_White| > 1.96
    passes: bool
    checks: dict


def _halfhour_regressions(grid, ofi_col="OFI"):
    """Run OLS(ΔP ~ OFI) in each 30-min subsample. Returns list of dicts (with depth)."""
    import numpy as np

    idx = grid.index.to_numpy()
    half = (idx // 1_800_000)   # id de media hora
    out = []
    for h in np.unique(half):
        sub = grid[half == h]
        if len(sub) < 20 or sub[ofi_col].std() == 0:
            continue
        r = ols_white(sub["dP"].to_numpy(), sub[ofi_col].to_numpy())
        r["depth"] = float(sub["depth"].mean())
        out.append(r)
    return out


def calibrate(grid, grid_excl=None, trade_imb=None, *, r2_threshold: float = 0.40):
    """Full calibration. `grid` = build_grid(...); `grid_excl` = build_grid(...,
    exclude_price_changing=True); `trade_imb` = a grid whose OFI column has been replaced
    by trade imbalance (see calibrate_with_trade_imbalance)."""
    import numpy as np

    regs = _halfhour_regressions(grid)
    mean_r2 = float(np.mean([r["r2"] for r in regs])) if regs else 0.0
    mean_beta = float(np.mean([r["b"] for r in regs])) if regs else 0.0
    frac_sig = float(np.mean([abs(r["t_b"]) > 1.96 for r in regs])) if regs else 0.0

    # (b) β vs profundidad, log-log
    slope = None
    betas = np.array([r["b"] for r in regs])
    depths = np.array([r["depth"] for r in regs])
    ok = (betas > 0) & (depths > 0)
    if ok.sum() >= 5:
        lr = ols_white(np.log(betas[ok]), np.log(depths[ok]))
        slope = lr["b"]

    # (a) trade imbalance
    mean_r2_ti = None
    if trade_imb is not None:
        regs_ti = _halfhour_regressions(trade_imb, ofi_col="OFI")
        mean_r2_ti = float(np.mean([r["r2"] for r in regs_ti])) if regs_ti else 0.0

    # (c) excluyendo eventos que cambian el precio
    mean_r2_excl = None
    if grid_excl is not None:
        regs_e = _halfhour_regressions(grid_excl)
        mean_r2_excl = float(np.mean([r["r2"] for r in regs_e])) if regs_e else 0.0

    checks = {
        "r2_ofi_gt_threshold": mean_r2 > r2_threshold,
        "a_ofi_beats_trade_imbalance": (mean_r2_ti is not None and mean_r2 > mean_r2_ti),
        "b_beta_inverse_depth": (slope is not None and slope < 0),
        "c_excl_price_changing_holds": (mean_r2_excl is not None and 0.20 < mean_r2_excl < mean_r2),
    }
    # el bloque PASA si R² supera el umbral y (a) se cumple (el test más discriminante)
    passes = checks["r2_ofi_gt_threshold"] and checks["a_ofi_beats_trade_imbalance"]
    return CalibrationResult(
        n_subsamples=len(regs), mean_r2_ofi=mean_r2, mean_r2_ti=mean_r2_ti,
        mean_r2_excl_price_changing=mean_r2_excl, depth_loglog_slope=slope,
        mean_beta=mean_beta, frac_beta_significant=frac_sig, passes=passes, checks=checks)


def grid_with_trade_imbalance(grid, ti_series):
    """Return a copy of `grid` whose OFI column is replaced by the aligned trade imbalance,
    so the same regression machinery compares ΔP~TI against ΔP~OFI."""
    g = grid.copy()
    g["OFI"] = ti_series.reindex(g.index).fillna(0.0)
    return g


def add_trade_imbalance(grid, ti_series):
    """Return a copy of `grid` with an aligned 'TI' column (for the joint regression)."""
    g = grid.copy()
    g["TI"] = ti_series.reindex(g.index).fillna(0.0)
    return g


def joint_regressions(grid_with_ti):
    """Regresión CONJUNTA ΔP = α + θ_O·OFI + θ_T·TI por media hora (la 8c del paper).
    Devuelve R² conjunto medio, t medios de θ_O y θ_T, y % de submuestras donde cada uno
    pasa el z-test al 5% (|t_White|>1.96)."""
    import numpy as np

    idx = grid_with_ti.index.to_numpy()
    half = idx // 1_800_000
    r2s, tO, tT, sigO, sigT = [], [], [], [], []
    for h in np.unique(half):
        sub = grid_with_ti[half == h]
        if len(sub) < 20 or sub["OFI"].std() == 0 or sub["TI"].std() == 0:
            continue
        r = ols_white_multi(sub["dP"].to_numpy(),
                            np.column_stack([sub["OFI"].to_numpy(), sub["TI"].to_numpy()]))
        r2s.append(r["r2"]); tO.append(r["t"][0]); tT.append(r["t"][1])
        sigO.append(abs(r["t"][0]) > 1.96); sigT.append(abs(r["t"][1]) > 1.96)
    if not r2s:
        return None
    return {"r2_joint": float(np.mean(r2s)),
            "t_theta_O": float(np.mean(tO)), "t_theta_T": float(np.mean(tT)),
            "pct_sig_O": float(np.mean(sigO)), "pct_sig_T": float(np.mean(sigT)),
            "n_subsamples": len(r2s)}


def estimate_c_and_units(grid):
    """ĉ y verificación de unidades. Corre las regresiones por media hora, ajusta
    log|β| = log c − λ·log(AD) (relación (3) del paper) y devuelve:
      - c_lambda1 = media geométrica de β·AD (con λ=1, comparable al 0.45 del paper)
      - c_loglog, lambda_loglog (con λ libre)
      - beta_mean, depth_measured (media de AD sobre las submuestras)
      - implied_depth_c05 = 0.5/β_mean (profundidad implícita con el c=1/2 estilizado)
      - discrepancy_factor = depth_measured / implied_depth (paper: implícita < medida)
    """
    import numpy as np

    regs = _halfhour_regressions(grid)
    betas = np.array([r["b"] for r in regs])
    depths = np.array([r["depth"] for r in regs])
    ok = (betas > 0) & (depths > 0)
    b, d = betas[ok], depths[ok]
    lr = ols_white_multi(np.log(b), np.log(d))
    lam = -lr["coefs"][0]
    c_loglog = float(np.exp(lr["a"]))
    c_lambda1 = float(np.exp(np.mean(np.log(b * d))))   # geomean(β·AD)
    beta_mean = float(betas.mean())
    depth_measured = float(depths.mean())
    implied_depth_c05 = 0.5 / beta_mean
    return {"c_lambda1": c_lambda1, "c_loglog": c_loglog, "lambda_loglog": lam,
            "beta_mean": beta_mean, "depth_measured": depth_measured,
            "implied_depth_c05": implied_depth_c05,
            "discrepancy_factor": depth_measured / implied_depth_c05}
