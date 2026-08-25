"""h008_redundancy_1day.py — H008 (4): coincidencia con la banda de vol de 1 DÍA.

Cierra bien la fila de Bollinger: la comparación previa era Bollinger(20 días) vs perfil de
1 día (desajuste de timescale). Ahora la banda de volatilidad se recomputa sobre la MISMA
ventana de 1 día del perfil (media ± 2σ de los precios intradía), y se compara con VAH/VAL.
Lee el resumen por-día (`results/crypto/h008_daily_summary.csv`) → funciona sobre la muestra
COMPLETA a medida que crece. Mismo criterio: tolerancia 10 bps, umbral 80% (condición 2).
"""

from __future__ import annotations

import csv
from pathlib import Path

SUMMARY = Path("results/crypto/h008_daily_summary.csv")
TOL_BPS = 10.0


def main():
    import numpy as np

    if not SUMMARY.exists():
        print("Sin resumen todavía (correr scripts.h008_build_summary)."); return
    rows = [r for r in csv.DictReader(open(SUMMARY)) if r["date"] < "2024-03-01"]  # in-sample
    n = len(rows)
    if n == 0:
        print("Resumen vacío."); return

    vah_band = np.array([abs(float(r["vah"]) - float(r["band_up"])) / float(r["poc"]) * 1e4 for r in rows])
    val_band = np.array([abs(float(r["val"]) - float(r["band_dn"])) / float(r["poc"]) * 1e4 for r in rows])
    poc_vwap = np.array([abs(float(r["poc"]) - float(r["vwap"])) / float(r["poc"]) * 1e4 for r in rows])

    def ci(d):
        k = int((d <= TOL_BPS).sum()); p = k / n; se = (p * (1 - p) / n) ** 0.5
        return k, p, max(0, p - 1.96 * se), min(1, p + 1.96 * se)

    print(f"# H008 — Coincidencia con banda de vol de 1 DÍA (muestra completa in-sample: {n} días-instrumento)\n")
    print("| comparación (1 día) | ≤10bps | % | IC95 | mediana | p75 | p90 |")
    print("|---|---|---|---|---|---|---|")
    for name, d in [("VAH ≈ banda_sup(1d, 2σ)", vah_band),
                    ("VAL ≈ banda_inf(1d, 2σ)", val_band),
                    ("POC ≈ VWAP(24h)", poc_vwap)]:
        k, p, lo, hi = ci(d)
        q = np.percentile(d, [50, 75, 90])
        print(f"| {name} | {k}/{n} | {p:.0%} | [{lo:.0%},{hi:.0%}] | {q[0]:.0f} | {q[1]:.0f} | {q[2]:.0f} | (bps)")
    any_hit = (vah_band <= TOL_BPS) | (val_band <= TOL_BPS) | (poc_vwap <= TOL_BPS)
    k = int(any_hit.sum()); p = k / n; se = (p * (1 - p) / n) ** 0.5
    lo, hi = max(0, p - 1.96 * se), min(1, p + 1.96 * se)
    print(f"| **cualquiera** | {k}/{n} | **{p:.0%}** | [{lo:.0%},{hi:.0%}] | — | — | — |")
    print()
    if lo > 0.80:
        print("VEREDICTO (2): coincidencia > 80% → H008 MUERTA por REDUNDANCIA.")
    elif hi < 0.80:
        print("VEREDICTO (2): coincidencia < 80% → (2) NO dispara; adelante Bloque 4.")
    else:
        print("VEREDICTO (2): IC cruza 80% → no concluyente.")


if __name__ == "__main__":
    main()
