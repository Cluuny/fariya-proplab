"""report.py — Capa de reporte.

Regenera, de forma determinista y con un solo comando, el resumen de desempeño
de una estrategia: equity curve, Sharpe, max drawdown y distribución de
retornos. Reproducibilidad total: mismas entradas -> mismo reporte.

Salida en markdown por defecto (legible y diffeable).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src import config, engine


def equity_curve(returns: pd.Series) -> pd.Series:
    """Curva de capital (base 1.0) a partir de retornos simples."""
    return (1.0 + returns.fillna(0.0)).cumprod()


def max_drawdown(returns: pd.Series) -> float:
    """Máximo drawdown (fracción negativa, p. ej. -0.23) de la equity curve."""
    eq = equity_curve(returns)
    peak = eq.cummax()
    dd = eq / peak - 1.0
    return float(dd.min()) if len(dd) else 0.0


def return_distribution(returns: pd.Series, bins: int = 10) -> pd.Series:
    """Histograma de retornos: conteo por bucket (determinista)."""
    r = returns.replace([np.inf, -np.inf], np.nan).dropna()
    if r.empty:
        return pd.Series(dtype=int)
    counts, edges = np.histogram(r.to_numpy(), bins=bins)
    labels = [f"[{edges[i]:+.4f}, {edges[i + 1]:+.4f})" for i in range(len(counts))]
    return pd.Series(counts, index=labels, name="count")


def metrics(returns: pd.Series) -> dict:
    """Métricas mínimas del reporte."""
    eq = equity_curve(returns)
    return {
        "n_obs": int(returns.dropna().shape[0]),
        "sharpe": engine.sharpe(returns),
        "max_drawdown": max_drawdown(returns),
        "total_return": float(eq.iloc[-1] - 1.0) if len(eq) else 0.0,
        "mean_daily": float(returns.mean()) if len(returns) else 0.0,
        "std_daily": float(returns.std(ddof=0)) if len(returns) else 0.0,
        "final_equity": float(eq.iloc[-1]) if len(eq) else 1.0,
    }


def render_challenge(result) -> str:
    """Sección markdown con los resultados del simulador de barrera."""
    lines = [
        "## Challenge (simulador de barrera)",
        "",
        "| Métrica | Valor |",
        "|---|---|",
        f"| P(pasar fase 1) | {result.p_phase1:.4f} |",
        f"| P(fallar fase 1) | {result.p_fail:.4f} |",
        f"| P(sin absorber fase 1) | {result.p_unresolved:.4f} |",
        f"| P(pasar fase 2) | {result.p_phase2:.4f} |",
        f"| P(pasar ambas) | {result.p_both:.4f} |",
        f"| Días esperados hasta pasar | {result.expected_days_to_pass:.1f} |",
        f"| P(quemar antes del payout N) | {result.p_burn_before_payout:.4f} |",
        f"| Valor esperado neto de cuotas | {result.expected_net_value:.2f} |",
        f"| Apalancamiento óptimo (decisión) | {result.optimal_leverage:.2f}× |",
        f"| Horizonte (días) | {result.horizon_days} |",
        "",
    ]
    if result.leverage_grid.size:
        lines += [
            "### Curva de apalancamiento",
            "",
            "P(pasar) es diagnóstica (monótona con horizonte honesto); el óptimo de "
            "**decisión** se elige por valor esperado neto, que pone precio al tiempo.",
            "",
            "| Leverage | P(ambas) | Valor neto |",
            "|---|---|---|",
        ]
        val = result.leverage_value_curve
        for i, (k, p) in enumerate(zip(result.leverage_grid, result.leverage_pass_curve)):
            v = f"{val[i]:.0f}" if i < len(val) else "—"
            mark = "  ← óptimo" if abs(k - result.optimal_leverage) < 1e-9 else ""
            lines.append(f"| {k:.2f}× | {p:.4f} | {v}{mark} |")
        lines.append("")
    return "\n".join(lines)


def render(returns: pd.Series, name: str = "strategy", challenge_result=None) -> str:
    """Reporte markdown determinista (sin timestamps).

    Si se pasa `challenge_result` (de challenge.simulate_challenge), se anexa la
    sección del simulador de barrera.
    """
    m = metrics(returns)
    lines = [
        f"# Reporte de desempeño — {name}",
        "",
        "## Métricas",
        "",
        "| Métrica | Valor |",
        "|---|---|",
        f"| Observaciones | {m['n_obs']} |",
        f"| Sharpe (anualizado) | {m['sharpe']:.4f} |",
        f"| Max drawdown | {m['max_drawdown']:.4f} |",
        f"| Retorno total | {m['total_return']:.4f} |",
        f"| Equity final (base 1.0) | {m['final_equity']:.4f} |",
        f"| Media diaria | {m['mean_daily']:.6f} |",
        f"| Desv. estándar diaria | {m['std_daily']:.6f} |",
        "",
        "## Equity curve (muestreada)",
        "",
    ]
    eq = equity_curve(returns)
    if len(eq):
        # Muestrear hasta ~20 puntos para un reporte compacto y determinista.
        step = max(1, len(eq) // 20)
        sampled = eq.iloc[::step]
        lines.append("| Fecha | Equity |")
        lines.append("|---|---|")
        for ts, val in sampled.items():
            label = ts.date() if hasattr(ts, "date") else ts
            lines.append(f"| {label} | {val:.4f} |")
    lines += ["", "## Distribución de retornos", "", "| Bucket | Conteo |", "|---|---|"]
    for label, count in return_distribution(returns).items():
        lines.append(f"| {label} | {int(count)} |")
    lines.append("")
    if challenge_result is not None:
        lines.append(render_challenge(challenge_result))
    return "\n".join(lines)


def generate(
    returns: pd.Series,
    name: str = "strategy",
    out_dir: Path = config.RESULTS,
    challenge_result=None,
) -> Path:
    """Escribe el reporte a `results/<name>/report.md` y devuelve la ruta."""
    dest = out_dir / name
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / "report.md"
    path.write_text(render(returns, name, challenge_result=challenge_result), encoding="utf-8")
    return path


def _load_prices() -> pd.DataFrame | None:
    """Carga precios de cierre de `data/clean/` si existen, uno por columna."""
    files = sorted(config.DATA_CLEAN.glob("*.parquet"))
    if not files:
        return None
    cols = {}
    for f in files:
        df = pd.read_parquet(f)
        close = df["close"] if "close" in df.columns else df.iloc[:, 0]
        cols[f.stem] = close
    return pd.DataFrame(cols).sort_index()


def main() -> int:
    from src import signals

    prices = _load_prices()
    if prices is None:
        print(
            f"No hay parquets en {config.DATA_CLEAN}. Corre `python -m src.loaders` "
            "primero (con crudos en data/raw/)."
        )
        return 0
    weights = signals.buy_and_hold(prices)
    returns = engine.backtest(prices, weights)
    path = generate(returns, name="buy_and_hold")
    print(render(returns, name="buy_and_hold"))
    print(f"\nReporte escrito en {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
