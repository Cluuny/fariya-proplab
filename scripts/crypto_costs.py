"""crypto_costs.py — runner de Bloque 3: imprime la tabla de sharpe_bruto_requerido cripto.

Uso: python -m scripts.crypto_costs [--vol 0.60]
"""

from __future__ import annotations

import argparse

from src.crypto import cost_model as cm


def main(argv=None):
    p = argparse.ArgumentParser(description="Modelo de costes cripto (Bloque 3)")
    p.add_argument("--vol", type=float, default=cm.VOL_ANUAL_BTC, help="vol anual del instrumento")
    args = p.parse_args(argv)

    print(f"# Coste por unidad de riesgo (comisión round-trip / vol diaria {cm.VOL_DIARIA_BTC:.3f})")
    print(f"  taker {cm.coste_por_unidad_riesgo(0.0):.4f} · 50% maker "
          f"{cm.coste_por_unidad_riesgo(0.5):.4f} · maker {cm.coste_por_unidad_riesgo(1.0):.4f}"
          f"   (pivote: taker ~0.033, MES ~0.063)")
    print()
    print(f"# Sharpe bruto requerido cripto (vol_anual={args.vol:.2f}, umbral neto {cm.UMBRAL_NETO})")
    print(f"{'trades/día':>10} {'maker':>7} {'funding@corte':>13} {'bruto_req':>10}")
    for r in cm.tabla_requerido(vol_anual=args.vol):
        print(f"{r['trades_dia']:>10} {r['fraccion_maker']*100:>6.0f}% "
              f"{r['funding_en_corte']:>13} {r['bruto_requerido']:>10.2f}")


if __name__ == "__main__":
    main()
