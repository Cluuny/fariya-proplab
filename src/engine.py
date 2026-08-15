"""engine.py — Motor de backtest.

Traduce pesos objetivo en retornos NETOS aplicando costos. Es el ÚNICO módulo
del sistema que aplica costos (comisión, spread, slippage, impacto).

Convención sin look-ahead: los pesos decididos al cierre del día t-1 capturan
el retorno del activo del día t. El costo de rotar se cobra el día en que
cambia el peso; la entrada inicial (de 0 al primer peso) se cobra el día 0.

Determinismo: mismas entradas (pesos, precios, costos) -> mismos retornos.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src import config


def _asset_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Retornos simples por activo (pct_change), primera fila = 0.

    Sanea valores no finitos: un precio en cero/no positivo (anomalía que
    loaders marca pero no corrige) produciría ±inf; se neutraliza a 0.0 para
    que un solo tick corrupto no propague inf a todo el backtest y el reporte.
    """
    ret = prices.pct_change()
    return ret.replace([np.inf, -np.inf], np.nan).fillna(0.0)


def _cost_rate(instrument: str, costs: dict[str, config.CostModel]) -> float:
    """Costo total por unidad de peso rotado para un instrumento."""
    cm = costs.get(instrument, config.DEFAULT_COST)
    return cm.spread + cm.slippage + cm.impact + cm.commission


def backtest(
    prices: pd.DataFrame,
    weights: pd.DataFrame,
    *,
    costs: dict[str, config.CostModel] | None = None,
    apply_costs: bool = True,
) -> pd.Series:
    """Devuelve la serie de retornos netos de la estrategia.

    - `prices`: precios por instrumento (columnas), indexado por fecha.
    - `weights`: pesos objetivo alineados a `prices` (mismas columnas).
    - `costs`: modelo de costos por instrumento; por defecto `config.COSTS`.
    - `apply_costs=False`: devuelve retornos BRUTOS (para comparación/tests).
    """
    if costs is None:
        costs = config.COSTS

    # Alinear pesos a las columnas/índice de precios.
    w = weights.reindex(index=prices.index, columns=prices.columns).fillna(0.0)
    asset_ret = _asset_returns(prices)

    # Retorno bruto: pesos del día anterior · retorno del activo hoy.
    gross = (w.shift(1).fillna(0.0) * asset_ret).sum(axis=1)

    if not apply_costs:
        return gross.rename("return")

    # Turnover por instrumento: |w_t - w_{t-1}|, con w_{-1}=0 (entrada inicial).
    turnover = (w - w.shift(1).fillna(0.0)).abs()
    rates = pd.Series(
        {col: _cost_rate(str(col), costs) for col in w.columns}
    )
    cost = turnover.mul(rates, axis=1).sum(axis=1)

    net = gross - cost
    return net.rename("return")


def sharpe(
    returns: pd.Series, *, periods_per_year: int = config.TRADING_DAYS_PER_YEAR
) -> float:
    """Sharpe anualizado (tasa libre de riesgo = 0)."""
    r = returns.dropna()
    sd = r.std(ddof=0)
    if sd == 0 or np.isnan(sd):
        return 0.0
    return float(np.sqrt(periods_per_year) * r.mean() / sd)
