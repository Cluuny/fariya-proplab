"""challenge.py — Simulador de barrera (EL NÚCLEO diferenciador).

El challenge de una cuenta de fondeo es un problema de primer paso con doble
barrera: P(tocar +objetivo antes de −límite), no un problema de trading. Este
módulo estima esa probabilidad y el valor económico esperado por simulación.

Método: block bootstrap (moving-block, NO i.i.d.) de los retornos diarios
netos que produce engine.py. Preserva autocorrelación y clustering de
volatilidad; un remuestreo i.i.d. subestimaría la volatilidad realista y daría
un P(pasar) optimista y falso (documento maestro sección 2.1).

Salidas (sección 3.4):
- P(pasar fase 1), P(pasar fase 2), P(pasar ambas)
- Días esperados hasta pasar
- P(quemar la cuenta fondeada antes del payout N)
- Valor esperado neto de cuotas  ← la métrica que decide
- Curva P(pasar) vs apalancamiento → multiplicador óptimo

Verificación: contra la fórmula analítica cerrada de primer paso con doble
barrera (ver `analytic_pass_probability`), no contra la intuición.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from src import config


# --------------------------------------------------------------------------- #
# Resultado                                                                    #
# --------------------------------------------------------------------------- #
# Resultados posibles de una trayectoria (contabilidad de tres resultados).
UNRESOLVED = 0  # llegó al horizonte sin tocar ninguna barrera
PASSED = 1      # alcanzó el objetivo
FAILED = 2      # tocó el límite diario o el drawdown máximo


@dataclass
class ChallengeResult:
    """Salidas del simulador de barrera."""

    p_phase1: float
    p_phase2: float
    p_both: float
    expected_days_to_pass: float
    p_burn_before_payout: float
    expected_net_value: float
    # Contabilidad de tres resultados de la fase 1 (suman 1 con p_phase1).
    p_fail: float = 0.0
    p_unresolved: float = 0.0
    horizon_days: int = 0
    leverage_grid: np.ndarray = field(default_factory=lambda: np.array([]))
    leverage_pass_curve: np.ndarray = field(default_factory=lambda: np.array([]))
    leverage_value_curve: np.ndarray = field(default_factory=lambda: np.array([]))
    optimal_leverage: float = 1.0


# --------------------------------------------------------------------------- #
# Block bootstrap                                                             #
# --------------------------------------------------------------------------- #
def block_bootstrap(
    returns: np.ndarray,
    *,
    n_paths: int,
    horizon: int,
    block_size: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Genera una matriz (n_paths, horizon) por moving-block bootstrap.

    Se eligen bloques contiguos de longitud `block_size` desde posiciones de
    inicio aleatorias (con wrap-around) y se concatenan hasta cubrir `horizon`.
    `block_size=1` equivale a i.i.d. (sólo para verificación analítica).
    """
    r = np.asarray(returns, dtype=float)
    n = r.size
    if n == 0:
        raise ValueError("returns vacío")
    if block_size < 1:
        raise ValueError("block_size debe ser >= 1")

    n_blocks = int(np.ceil(horizon / block_size))
    # Posiciones de inicio de cada bloque, para todas las trayectorias.
    starts = rng.integers(0, n, size=(n_paths, n_blocks))
    # Offsets dentro del bloque: 0..block_size-1
    offsets = np.arange(block_size)
    # Índices (n_paths, n_blocks, block_size) con wrap-around.
    idx = (starts[:, :, None] + offsets[None, None, :]) % n
    sampled = r[idx].reshape(n_paths, n_blocks * block_size)
    return sampled[:, :horizon]


# --------------------------------------------------------------------------- #
# Evaluación de barreras (first passage)                                      #
# --------------------------------------------------------------------------- #
def _first_passage(
    paths: np.ndarray, target: float, daily_loss_limit: float, max_drawdown: float
) -> tuple[np.ndarray, np.ndarray]:
    """Evalúa cada trayectoria y devuelve (outcome, day_index).

    `outcome` es un vector con la CONTABILIDAD DE TRES RESULTADOS:
    `PASSED` (tocó el objetivo), `FAILED` (tocó el límite diario o el drawdown
    máximo estático), o `UNRESOLVED` (llegó al final del horizonte sin tocar
    ninguna barrera). NUNCA se pliega UNRESOLVED en FAILED: plegarlo invertiría
    la conclusión del sistema (baja volatilidad tarda más en absorber y quedaría
    castigada como fracaso).

    El P&L se acumula de forma ADITIVA sobre el capital inicial (sizing estático
    relativo al balance inicial), que es lo que define un challenge: objetivo y
    drawdown se miden como fracción del capital INICIAL, no compuesto. Esto
    además coincide con la fórmula analítica de primer paso (proceso aditivo).

    Reglas, evaluadas por día:
    - PASA: pnl >= target
    - QUEMA: retorno diario <= -daily_loss_limit  (límite de pérdida diaria)
             o pnl <= -max_drawdown               (drawdown estático vs inicial)
    Gana el primer evento (first passage). `day_index` = día del evento de paso
    (o horizonte si no pasa).
    """
    n_paths, horizon = paths.shape
    level = np.zeros(n_paths)          # P&L acumulado (aditivo) vs capital inicial
    passed = np.zeros(n_paths, dtype=bool)
    burned = np.zeros(n_paths, dtype=bool)
    day_passed = np.full(n_paths, horizon, dtype=int)

    for t in range(horizon):
        active = ~passed & ~burned
        if not active.any():
            break
        r_t = paths[:, t]
        level = np.where(active, level + r_t, level)
        pnl = level

        # Quema: violación de límite diario o de drawdown estático.
        burn_now = active & ((r_t <= -daily_loss_limit) | (pnl <= -max_drawdown))
        burned |= burn_now

        # Pasa: alcanza el objetivo sin haber quemado este mismo día.
        pass_now = active & ~burn_now & (pnl >= target)
        newly = pass_now & ~passed
        day_passed = np.where(newly, t + 1, day_passed)
        passed |= pass_now

    # Contabilidad de tres resultados: quien no pasó ni quemó queda UNRESOLVED.
    outcome = np.full(n_paths, UNRESOLVED, dtype=np.int8)
    outcome[passed] = PASSED
    outcome[burned] = FAILED
    return outcome, day_passed


# --------------------------------------------------------------------------- #
# Simulador principal                                                         #
# --------------------------------------------------------------------------- #
def simulate_challenge(
    returns,
    *,
    rules: config.FirmRules = config.DEFAULT_FIRM_RULES,
    params: config.SimulatorParams = config.DEFAULT_SIM_PARAMS,
    leverage: float = 1.0,
    with_leverage_curve: bool = True,
) -> ChallengeResult:
    """Estima P(pasar) y métricas económicas de un challenge.

    `returns`: serie/array de retornos diarios netos (de engine.py).
    `leverage`: multiplicador aplicado a los retornos para esta corrida.
    """
    r = np.asarray(getattr(returns, "to_numpy", lambda: returns)(), dtype=float)
    r = r[np.isfinite(r)]
    if r.size == 0:
        raise ValueError("returns sin datos finitos")

    rng = np.random.default_rng(params.seed)
    scaled = r * leverage

    # --- Fase 1 ---
    paths1 = block_bootstrap(
        scaled,
        n_paths=params.n_bootstraps,
        horizon=params.horizon_days,
        block_size=params.block_size,
        rng=rng,
    )
    outcome1, days1 = _first_passage(
        paths1, rules.phase1_target, rules.daily_loss_limit, rules.max_drawdown
    )
    passed1 = outcome1 == PASSED
    p_phase1 = float(passed1.mean())
    p_fail1 = float((outcome1 == FAILED).mean())
    p_unresolved1 = float((outcome1 == UNRESOLVED).mean())

    # --- Fase 2 (independiente; P(ambas) = P1 * P2 condicional aprox.) ---
    paths2 = block_bootstrap(
        scaled,
        n_paths=params.n_bootstraps,
        horizon=params.horizon_days,
        block_size=params.block_size,
        rng=rng,
    )
    outcome2, days2 = _first_passage(
        paths2, rules.phase2_target, rules.daily_loss_limit, rules.max_drawdown
    )
    passed2 = outcome2 == PASSED
    p_phase2 = float(passed2.mean())
    p_both = p_phase1 * p_phase2

    # Días esperados hasta pasar ambas fases (condicionado a pasar). Si en alguna
    # fase nada pasa dentro del horizonte, se acota al horizonte total.
    if passed1.any() and passed2.any():
        expected_days = float(days1[passed1].mean() + days2[passed2].mean())
    else:
        expected_days = float(params.horizon_days * 2)

    # --- P(quemar cuenta fondeada antes del payout N) ---
    # Tras fondeo, cada ciclo de payout es como sobrevivir sin violar DD/daily.
    # Reusar fase 2 como proxy de "ciclo de payout": quemar = no sobrevivir.
    p_survive_cycle = p_phase2
    p_burn_before_payout = float(1.0 - p_survive_cycle**rules.n_payouts)

    # --- Valor esperado neto de cuotas (pone precio al tiempo) ---
    expected_net = _expected_net_value(
        p_both, p_burn_before_payout, expected_days, rules
    )

    result = ChallengeResult(
        p_phase1=p_phase1,
        p_phase2=p_phase2,
        p_both=p_both,
        expected_days_to_pass=expected_days,
        p_burn_before_payout=p_burn_before_payout,
        expected_net_value=expected_net,
        p_fail=p_fail1,
        p_unresolved=p_unresolved1,
        horizon_days=int(params.horizon_days),
    )

    # --- Curva de apalancamiento ---
    # Se reporta la curva P(pasar) como DIAGNÓSTICO (monótona decreciente en
    # leverage con horizonte honesto), pero el apalancamiento de DECISIÓN sale
    # de maximizar el valor esperado neto, que pone precio al tiempo/capital
    # inmovilizado del bajo apalancamiento. argmax(P) daría el leverage mínimo.
    if with_leverage_curve:
        grid = np.arange(
            params.leverage_min,
            params.leverage_max + params.leverage_step / 2,
            params.leverage_step,
        )
        sub = [
            simulate_challenge(
                r, rules=rules, params=params, leverage=float(k),
                with_leverage_curve=False,
            )
            for k in grid
        ]
        result.leverage_grid = grid
        result.leverage_pass_curve = np.array([s.p_both for s in sub])
        result.leverage_value_curve = np.array([s.expected_net_value for s in sub])
        result.optimal_leverage = float(grid[int(np.argmax(result.leverage_value_curve))])

    return result


def _expected_net_value(
    p_both: float,
    p_burn_before_payout: float,
    expected_days: float,
    rules: config.FirmRules,
) -> float:
    """Valor esperado neto de cuotas — pone precio al tiempo.

    - Nº esperado de intentos hasta pasar ambas fases ~ geométrica: 1/P(ambas).
    - Costo de cuotas = intentos · fee.
    - Costo del tiempo = días esperados (por intento) · intentos · costo diario
      de capital inmovilizado. Este término es lo que hace que el óptimo de
      apalancamiento sea INTERIOR: sin él, bajar el leverage sólo subiría P y el
      óptimo caería en el mínimo (esperar casi infinito).
    - Ingreso tras fondeo = payout esperado ponderado por sobrevivir al payout.

    Supuesto económico explícito: `rules.daily_capital_cost` es el costo de
    oportunidad diario del capital mientras se intenta el challenge.
    """
    if p_both <= 0:
        # Nunca pasa dentro del horizonte: sólo se acumulan cuotas y tiempo.
        return -1e12
    expected_attempts = 1.0 / p_both
    expected_fee_cost = expected_attempts * rules.fee
    expected_time_cost = expected_attempts * expected_days * rules.daily_capital_cost
    expected_income = (1.0 - p_burn_before_payout) * rules.payout_per_cycle * rules.n_payouts
    return float(expected_income - expected_fee_cost - expected_time_cost)


# --------------------------------------------------------------------------- #
# Oráculo analítico (verificación, no motor)                                  #
# --------------------------------------------------------------------------- #
def analytic_pass_probability(mu: float, sigma: float, a: float, b: float) -> float:
    """Fórmula cerrada de primer paso con doble barrera.

    P(tocar +b antes de −a) para una deriva `mu` y volatilidad `sigma`:
        P = [1 − e^(−2μa/σ²)] / [1 − e^(−2μ(a+b)/σ²)]
    Con μ=0 el límite es a/(a+b) (0.5 si a=b).
    """
    if sigma <= 0:
        raise ValueError("sigma debe ser > 0")
    if mu == 0:
        return a / (a + b)
    k = 2.0 * mu / (sigma**2)
    return float((1.0 - np.exp(-k * a)) / (1.0 - np.exp(-k * (a + b))))
