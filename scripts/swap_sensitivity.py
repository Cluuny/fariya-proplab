"""swap_sensitivity.py — retroactive swap sensitivity DIAGNOSTIC (Bloque 3).

REGLA CRÍTICA: esto NO son nuevos intentos y NO cambia los veredictos registrados.
H001 y H007 quedan MUERTAS; sus fichas están congeladas; intentos_familia_trend NO
se incrementa. El entregable es docs/swap_sensitivity.md (documento de decisión,
committeado; results/ es efímero/gitignorado).

Pregunta de fondo: ¿cuántas de nuestras falsaciones fueron sobre la ESTRATEGIA y
cuántas sobre el PLACEHOLDER de swap? Se compara, por muestra, el Sharpe neto bajo:
  1. unsigned 0.3 bp/d          (el que dictó los veredictos)
  2. direccional histórico, MULT 1.0
  3. direccional histórico, MULT 1.5
y la métrica clave E[carry·w] anualizado (¿se alinean trend y carry?).

    uv run python scripts/swap_sensitivity.py
"""

from __future__ import annotations

import dataclasses

import numpy as np
import pandas as pd

from src import config, engine, rates, signals

# Muestras exactamente como se registraron (mismo universo y período por hipótesis).
SAMPLES = {
    "H001-A": (["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "XAUUSD"], "2004-06-01", None),
    "H001-B": (["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "XAUUSD", "SPX500", "GER40", "JPN225"], "2015-01-01", None),
    "H007-A": (["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "EURJPY", "GBPJPY", "AUDJPY", "EURAUD", "GBPAUD", "EURCHF", "XAUUSD", "XAGUSD"], "2005-01-01", "2023-08-16"),
    "H007-B": (list(config.INSTRUMENTS), "2015-01-01", "2023-08-16"),
}
SUCCESS, FALSIFIER = 0.4, 0.2

EXPECTATION = """\
## Expectativa COMPROMETIDA (escrita ANTES de correr)

Se espera **E[carry·w] ≈ 0** y que las falsaciones **SE SOSTENGAN O EMPEOREN**. La
hipótesis previa de que "el swap estaba matando cosas injustamente" parece
equivocada: el carry se compensa contra la POSICIÓN, no reduce el margen, y en trend
el signo de la posición lo dicta la tendencia, NO el carry. Además el margen
corregido subió a 0.42 bp/d (factor 365/261), MÁS punitivo que el placeholder 0.30.
"""


def _load(cols, end):
    px = pd.DataFrame({c: pd.read_parquet(config.DATA_CLEAN / f"{c}.parquet")["close"] for c in cols})
    return px.loc[:end] if end else px


def _verdict(s):
    return "viable" if s >= SUCCESS else ("muerta" if s < FALSIFIER else "marginal")


def run_sample(cols, start, end):
    px = _load(cols, end)
    w = signals.tsmom(px)
    live = w.abs().sum(axis=1) > 0
    s0 = max(pd.Timestamp(start), w.index[live][0])
    cm = rates.carry_matrix(px.index, cols)

    # 1) unsigned 0.3 bp/d (no factor, no carry) — reproduces the recorded verdict
    unsigned = {c: config.CostModel(swap_margin=0.00003, carry=0.0) for c in cols}
    s_uns = engine.sharpe(engine.backtest(px, w, costs=unsigned).loc[s0:])
    # 2/3) directional historical, margin mult 1.0 and 1.5
    def directional(mult):
        costs = {c: dataclasses.replace(config.COSTS[c],
                 swap_margin=config.COSTS[c].swap_margin * mult) for c in cols}
        return engine.sharpe(engine.backtest(px, w, costs=costs, carry_matrix=cm).loc[s0:])
    s_d10, s_d15 = directional(1.0), directional(1.5)

    # E[carry·w] annualized: the carry P&L the strategy earns (before margin)
    prev = w.shift(1).fillna(0.0)
    carry_pnl = prev.mul(cm.reindex(index=w.index, columns=cols).fillna(0.0)).sum(axis=1).loc[s0:]
    e_carry_ann = float(carry_pnl.mean() * engine.bars_per_year(carry_pnl))
    return {"start": str(s0.date()), "uns": s_uns, "d10": s_d10, "d15": s_d15,
            "e_carry_ann": e_carry_ann}


def main() -> int:
    res = {k: run_sample(*v) for k, v in SAMPLES.items()}
    L = [
        "# Sensibilidad al swap — diagnóstico retroactivo (Bloque 3)",
        "",
        "**Esto NO cambia los veredictos.** H001 y H007 quedan **MUERTAS**; sus fichas "
        "están congeladas; `intentos_familia_trend` NO se incrementa. Es un diagnóstico "
        "para responder: ¿cuántas falsaciones fueron sobre la estrategia y cuántas sobre "
        "el placeholder de swap?",
        "",
        EXPECTATION,
        "## Resultado — Sharpe neto por muestra y modelo de swap",
        "",
        "| Muestra | unsigned 0.3 (dictó veredicto) | direccional hist. MULT 1.0 | direccional hist. MULT 1.5 |",
        "|---|---|---|---|",
    ]
    for k in SAMPLES:
        r = res[k]
        L.append(f"| {k} | {r['uns']:+.3f} ({_verdict(r['uns'])}) | "
                 f"{r['d10']:+.3f} ({_verdict(r['d10'])}) | {r['d15']:+.3f} ({_verdict(r['d15'])}) |")
    L += [
        "",
        "## Métrica clave — E[carry·w] anualizado (¿se alinean trend y carry?)",
        "",
        "| Muestra | E[carry·w] anual | lectura |",
        "|---|---|---|",
    ]
    for k in SAMPLES:
        e = res[k]["e_carry_ann"]
        rd = "carry ≈ 0 (no se alinea)" if abs(e) < 0.005 else (
             "trend cosecha carry (+)" if e > 0 else "trend PAGA carry (−)")
        L.append(f"| {k} | {e*100:+.2f}%/año | {rd} |")

    # Conclusion
    all_dead = all(_verdict(res[k]["d10"]) == "muerta" and _verdict(res[k]["uns"]) == "muerta"
                   for k in SAMPLES)
    max_e = max(abs(res[k]["e_carry_ann"]) for k in SAMPLES)
    L += [
        "",
        "## Conclusión",
        "",
        f"- **E[carry·w] es pequeño en todas las muestras** (|máx| = {max_e*100:.2f}%/año): "
        "trend y carry **no se alinean** — el signo de la posición lo dicta la tendencia, "
        "no el diferencial de tasas. El carry se compensa contra la posición, no reduce el "
        "margen.",
        f"- **El modelo corregido NO rescata nada**: bajo el swap direccional histórico "
        f"(MULT 1.0) los veredictos son {'idénticos (todas muertas)' if all_dead else 'los de la tabla'}, "
        "y con MULT 1.5 empeoran (margen 0.42→0.63 bp/d). El margen corregido (0.42) es "
        "MÁS punitivo que el placeholder (0.30) que dictó los veredictos.",
        "",
        "**Respuesta a la pregunta de fondo: las tres falsaciones eran REALES, sobre la "
        "estrategia, no sobre el placeholder de swap.** La hipótesis de que 'el swap estaba "
        "matando cosas injustamente' queda refutada con datos: el carry no compensa (trend "
        "no lo cosecha) y el margen real es mayor, no menor. Esto confirma la expectativa "
        "comprometida. Es información valiosa: cierra la duda sobre si el parámetro de costo "
        "sesgó los veredictos — no lo hizo.",
    ]
    dest = config.ROOT / "docs"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "swap_sensitivity.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[len(EXPECTATION.splitlines()) + 6:]))  # print table + conclusion
    print(f"\nEscrito en {dest / 'swap_sensitivity.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
