"""h008_coincidence.py — H008 Bloque 3.3: diagnóstico de COINCIDENCIA (condición 2 del falsador).

Para cada día de la muestra IN-SAMPLE (excluye el holdout 2024-03-01→2024-08-31), construye el
perfil (VAH/VAL/POC, bucket $10, área 70%) y los niveles SIMPLES (máx/mín del día = N=1), y mide:

  % de días con |VAH − máx| / mid ≤ 10 bps   (VAH ≈ máximo)
  % de días con |VAL − mín| / mid ≤ 10 bps   (VAL ≈ mínimo)

Si la coincidencia (cualquiera de las dos, o combinada) > 80% → H008 MUERE por REDUNDANCIA
(condición 2), sin construir estrategia. NO requiere backtest ni tocar el holdout.
"""

from __future__ import annotations

from pathlib import Path

from src.crypto import volume_profile as vp

AGG_DIR = "data/raw_crypto/futures/um/daily/aggTrades"
HOLDOUT_START = "2024-03-01"     # ficha: corte del holdout; NO se lee aquí
TOL_BPS = 10.0


def _insample_days(symbol: str):
    d = Path(AGG_DIR) / symbol
    if not d.exists():
        return []
    days = []
    for f in sorted(d.glob(f"{symbol}-aggTrades-*.zip")):
        date = f.stem.replace(f"{symbol}-aggTrades-", "")
        if date < HOLDOUT_START:            # excluir holdout FÍSICAMENTE por fecha
            days.append((date, f))
    return days


def main():
    import numpy as np

    rows = []
    for sym in ("BTCUSDT", "ETHUSDT"):
        for date, f in _insample_days(sym):
            p = vp.profile_from_zip(f)
            mid = p.poc
            vah_bps = abs(p.vah - p.high) / mid * 1e4
            val_bps = abs(p.val - p.low) / mid * 1e4
            rows.append({"sym": sym, "date": date, "vah_bps": vah_bps, "val_bps": val_bps,
                         "va_frac": p.va_volume_frac})

    n = len(rows)
    if n == 0:
        print("Sin días in-sample descargados.")
        return
    vah_hit = sum(1 for r in rows if r["vah_bps"] <= TOL_BPS)
    val_hit = sum(1 for r in rows if r["val_bps"] <= TOL_BPS)
    either = sum(1 for r in rows if r["vah_bps"] <= TOL_BPS or r["val_bps"] <= TOL_BPS)

    def ci(k):
        p = k / n
        se = (p * (1 - p) / n) ** 0.5
        return p, max(0, p - 1.96 * se), min(1, p + 1.96 * se)

    print(f"# H008 — Diagnóstico de coincidencia (in-sample, {n} días-instrumento, tol {TOL_BPS:.0f} bps)\n")
    print(f"días BTC+ETH in-sample (< {HOLDOUT_START}): {n}\n")
    print("| coincidencia | n_hit | % | IC95 |")
    print("|---|---|---|---|")
    for name, k in [("VAH ≈ máximo", vah_hit), ("VAL ≈ mínimo", val_hit), ("cualquiera de las dos", either)]:
        p, lo, hi = ci(k)
        print(f"| {name} | {k}/{n} | {p:.0%} | [{lo:.0%}, {hi:.0%}] |")
    print(f"\nmediana |VAH−máx|: {np.median([r['vah_bps'] for r in rows]):.0f} bps · "
          f"mediana |VAL−mín|: {np.median([r['val_bps'] for r in rows]):.0f} bps")
    _, elo, ehi = ci(either)
    print()
    if elo > 0.80:
        print("VEREDICTO condición (2): coincidencia > 80% con IC que no cruza → H008 MUERTA por REDUNDANCIA.")
    elif ehi < 0.80:
        print("VEREDICTO condición (2): coincidencia < 80% con IC que no cruza → (2) NO dispara; "
              "procede el Bloque 4 (estrategia) — como change SIGUIENTE.")
    else:
        print("VEREDICTO condición (2): IC de la coincidencia cruza 80% → no concluyente en (2); "
              "más días o decisión explícita.")


if __name__ == "__main__":
    main()
