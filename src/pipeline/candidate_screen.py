"""candidate_screen.py — cribado ARITMÉTICO de un candidato que superó E3, sin backtest.

Mismo patrón que el cribado A.4 de H002 y el de COT: tres o cuatro números que suelen cerrar un
candidato GRATIS, antes de gastar un intento o escribir una ficha. No corre estrategias; sólo
aritmética sobre el Sharpe reportado y el espacio de búsqueda.

Piezas (todas stdlib, `statistics.NormalDist` para el inverso normal):
  - sharpe_se / sharpe_ci: error estándar de un Sharpe estimado (Lo 2002) y su IC.
  - expected_max_sharpe: el Sharpe MÁXIMO esperado por AZAR bajo N ensayos de edge cero
    (deflación de Bailey & López de Prado 2014). Si el observado no lo supera, es suerte de
    búsqueda.
  - effective_breadth: N instrumentos correlacionados → amplitud efectiva N/(1+(N-1)ρ).
"""

from __future__ import annotations

import math
from statistics import NormalDist

_N = NormalDist()
EULER_GAMMA = 0.5772156649015329


def sharpe_se(sr: float, n_obs: int) -> float:
    """Error estándar de un Sharpe estimado sobre `n_obs` observaciones a la MISMA frecuencia que
    `sr` (Lo 2002, retornos iid): SE ≈ √((1 + SR²/2) / n)."""
    if n_obs <= 1:
        return float("inf")
    return math.sqrt((1.0 + 0.5 * sr * sr) / n_obs)


def sharpe_se_annual(sr_annual: float, n_years: float, periods_per_year: int = 12) -> float:
    """SE de un Sharpe ANUALIZADO estimado sobre `n_years` años con `periods_per_year` obs/año.
    Se computa a la frecuencia de las observaciones y se reanualiza (×√periods)."""
    n_obs = int(round(n_years * periods_per_year))
    sr_period = sr_annual / math.sqrt(periods_per_year)
    return sharpe_se(sr_period, n_obs) * math.sqrt(periods_per_year)


def sharpe_ci(sr: float, se: float, z: float = 1.96) -> tuple[float, float]:
    return (sr - z * se, sr + z * se)


def expected_max_sharpe(n_trials: int, se: float) -> float:
    """Sharpe MÁXIMO esperado por azar bajo `n_trials` ensayos independientes de edge cero
    (Bailey & López de Prado 2014, «The Deflated Sharpe Ratio»):

        E[max] ≈ SE · [ (1−γ)·Z⁻¹(1 − 1/N) + γ·Z⁻¹(1 − 1/(N·e)) ]

    Si el Sharpe observado no supera este umbral, es indistinguible de suerte de búsqueda."""
    if n_trials < 2:
        return 0.0
    z1 = _N.inv_cdf(1.0 - 1.0 / n_trials)
    z2 = _N.inv_cdf(1.0 - 1.0 / (n_trials * math.e))
    return se * ((1.0 - EULER_GAMMA) * z1 + EULER_GAMMA * z2)


def effective_breadth(n_instruments: int, rho: float) -> float:
    """Amplitud efectiva de N instrumentos equicorrelacionados a ρ: N / (1 + (N−1)·ρ).
    A ρ alto colapsa hacia 1 (los sectores co-mueven → casi una sola apuesta)."""
    if n_instruments <= 0:
        return 0.0
    return n_instruments / (1.0 + (n_instruments - 1) * rho)


def deflation_screen(sr_obs: float, se: float, liston: float, n_trials_grid) -> list[dict]:
    """Para cada N del grid: el umbral de suerte E[max] y si el observado lo supera Y supera el
    listón. Un candidato 'muere' por deflación si a un N plausible E[max] ≥ min(sr_obs, ...) o el
    deflactado (sr_obs − E[max] + ruido) cae bajo el listón."""
    out = []
    for n in n_trials_grid:
        emax = expected_max_sharpe(n, se)
        out.append({
            "n_trials": n,
            "umbral_suerte": emax,
            "supera_suerte": sr_obs > emax,
            "umbral_sobre_liston": emax >= liston,   # a este N, la suerte ya alcanza el listón
        })
    return out
