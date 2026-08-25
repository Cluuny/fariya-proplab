"""h008_backtest.py — H008 Bloque 4: estrategia condicional, ramas pareadas, nulo.

La ficha está congelada. Estrategia pre-registrada:
  contexto: (high−low)_prev / ATR(14) < 1.0 (balance)
  trigger:  extensión fuera del VA previo + rechazo (mid re-entra en ≤3 barras de 1m)
  entrada:  límite (maker) en el borde; short si arriba del VAH, long si abajo del VAL
  salida:   objetivo POC, stop 1× rango del VA más allá del borde, time-stop al cierre 24h

Dos ramas PAREADAS (mismos episodios, definidos por el CONTEXTO, no por los niveles):
  (a) PERFIL: entra en VAH/VAL, objetivo POC
  (b) SIMPLE: entra en la banda de vol de 1 día, objetivo VWAP(24h)

SUPUESTO DE FILLS (D5): la orden es límite; con 1m sólo se ve si el precio TOCÓ el nivel, no
si se habría llenado. `fill_bps`=0 → fill al toque (infla el resultado); `fill_bps`=5 → fill sólo
si el precio CRUZA el nivel por ≥5 bps (más estricto). El modelo de fills real nunca se construyó.
"""

from __future__ import annotations

from dataclasses import dataclass

from src import costs_model as cm
from src.crypto import cost_model as ccm

K_BARS = 3
MAKER = ccm.MAKER_FEE          # 0.0002
TAKER = ccm.TAKER_FEE          # 0.0005
FUNDING_HOURS = (0, 8, 16)     # cortes UTC


@dataclass
class Trade:
    filled: bool
    ret_net: float = 0.0
    exit_type: str = ""         # target | stop | timestop
    crossed_funding: bool = False


def _crosses_funding(t0_ms: int, t1_ms: int) -> bool:
    """¿el intervalo [t0,t1] (ms UTC) cruza un corte 00/08/16?"""
    h0 = (t0_ms // 3_600_000)
    h1 = (t1_ms // 3_600_000)
    for h in range(int(h0), int(h1) + 1):
        if (h % 24) in FUNDING_HOURS and h * 3_600_000 >= t0_ms:
            return True
    return False


def simulate(bars, entry_level, target, va_range, direction, *, fill_bps=0.0,
             funding_rate=ccm.FUNDING_PER_INTERVAL_DEFAULT):
    """`bars`: array (n,4) [t_ms, high, low, close] del día, ordenado. `direction`: 'short'/'long'.
    Devuelve Trade (neto de comisión + funding si cruza corte)."""
    import numpy as np

    t = bars[:, 0]; hi = bars[:, 1]; lo = bars[:, 2]; cl = bars[:, 3]
    adj = entry_level * fill_bps / 1e4
    if direction == "short":
        fillmask = hi >= entry_level + adj          # el precio sube hasta el nivel (+margen)
        stop_level = entry_level + va_range
    else:
        fillmask = lo <= entry_level - adj
        stop_level = entry_level - va_range
    idx = np.where(fillmask)[0]
    if len(idx) == 0:
        return Trade(filled=False)
    i = int(idx[0])
    entry = entry_level
    # simular hacia adelante desde i+1
    exit_price = cl[-1]; exit_type = "timestop"; exit_i = len(bars) - 1
    for j in range(i + 1, len(bars)):
        if direction == "short":
            if lo[j] <= target:
                exit_price, exit_type, exit_i = target, "target", j; break
            if hi[j] >= stop_level:
                exit_price, exit_type, exit_i = stop_level, "stop", j; break
        else:
            if hi[j] >= target:
                exit_price, exit_type, exit_i = target, "target", j; break
            if lo[j] <= stop_level:
                exit_price, exit_type, exit_i = stop_level, "stop", j; break
    gross = (entry - exit_price) / entry if direction == "short" else (exit_price - entry) / entry
    # comisión: entrada maker; salida maker si target, taker si stop/timestop
    fee = MAKER + (MAKER if exit_type == "target" else TAKER)
    crossed = _crosses_funding(int(t[i]), int(t[exit_i]))
    fund = funding_rate if crossed else 0.0
    return Trade(filled=True, ret_net=gross - fee - fund, exit_type=exit_type, crossed_funding=crossed)


def sharpe_active(returns, episodes_per_year):
    import numpy as np
    r = np.asarray(returns, float)
    if len(r) < 2 or r.std(ddof=0) == 0:
        return 0.0
    return float(r.mean() / r.std(ddof=0) * np.sqrt(episodes_per_year))


def sharpe_full(returns, episodes_per_year, total_day_instruments):
    """Sharpe de serie completa ≈ Sharpe activo × √duty (dilución sobre los días flat).
    duty ≈ n_episodios / total_días-instrumento."""
    import numpy as np
    n = len(returns)
    duty = n / total_day_instruments if total_day_instruments else 0.0
    return sharpe_active(returns, episodes_per_year) * np.sqrt(duty)
