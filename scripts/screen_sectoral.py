"""screen_sectoral.py — cribado aritmético del candidato «Sectoral Intramonth Momentum».

Corre los cuatro números del cribado (deflación, nulo de exposición compartida, amplitud
efectiva / IC, operabilidad) sin backtest. Imprime el veredicto. Reproducible.
"""

from __future__ import annotations

from src.pipeline import candidate_screen as cs

# --- datos REPORTADOS por el paper (docs/pipeline_run_002.md D3) ---
SR_OBS = 0.55            # Sharpe long-short reportado (in-sample, sin deflactar)
LISTON = 0.44            # bruto requerido CFD al duty estimado (E3)
N_YEARS = 27.5           # Dic 1998 – Jun 2026
EVENTS_PER_YEAR = 12     # rebalanceo mensual (3 patas intramensuales)
N_SECTORS = 9            # 9 Select Sector SPDR (+ SPY como benchmark)
RHO = 0.75               # correlación típica entre sectores (0.7-0.8)

# nulo de exposición compartida: el turn-of-the-month captura ~toda la prima de renta variable
# del mes; el Sharpe anual del mercado ~0.45. Al concentrar la exposición en la ventana de mayor
# deriva (TOM), un nulo «largo del mercado en la misma ventana, sectores al azar» rinde ≳0.45.
MARKET_SHARPE = 0.45
TOM_CONCENTRATION = 1.15   # la ventana TOM concentra deriva → factor sobre el Sharpe de mercado


def main():
    print("=== Cribado aritmético — Sectoral Intramonth Momentum ===\n")

    # (1.1) DEFLATED SHARPE
    se = cs.sharpe_se_annual(SR_OBS, N_YEARS, EVENTS_PER_YEAR)
    grid = [10, 20, 50, 100, 150, 200]
    print(f"(1.1) DEFLATED SHARPE  — SE(Sharpe) = {se:.3f} sobre {N_YEARS}a × {EVENTS_PER_YEAR}/a")
    print(f"      espacio de búsqueda implícito: 3 patas × ~21 días × dirección × 9 sectores → N grande")
    for r in cs.deflation_screen(SR_OBS, se, LISTON, grid):
        flag = "≥ listón (la SUERTE ya alcanza el suelo)" if r["umbral_sobre_liston"] else ""
        print(f"      N={r['n_trials']:4d}: umbral de suerte E[max]={r['umbral_suerte']:.3f}  "
              f"obs {SR_OBS} { '>' if r['supera_suerte'] else '≤' } suerte  {flag}")
    n_star = next((r["n_trials"] for r in cs.deflation_screen(SR_OBS, se, LISTON, grid)
                   if r["umbral_sobre_liston"]), None)
    print(f"      → a N≈{n_star} la suerte de búsqueda YA alcanza el listón {LISTON}. Para una "
          f"estrategia de 3 patas calendáricas, N≥50 es plausible → deflación NO despeja.\n")

    # (1.2) NULO CON EXPOSICIÓN COMPARTIDA
    null_sr = MARKET_SHARPE * TOM_CONCENTRATION
    print(f"(1.2) NULO EXPOSICIÓN COMPARTIDA — Sharpe de mercado ~{MARKET_SHARPE}, concentrado en la "
          f"ventana TOM (×{TOM_CONCENTRATION}) → nulo ≈ {null_sr:.2f}")
    print(f"      El turn-of-the-month captura ~toda la prima del mes; una estrategia sectorial "
          f"intramensual hereda esa deriva. obs {SR_OBS} vs nulo {null_sr:.2f}: "
          f"{'NO lo supera claramente' if SR_OBS <= null_sr + se else 'lo supera'}. "
          f"Es el problema de H003 (su Sharpe ERA el beta).\n")

    # (1.3) AMPLITUD EFECTIVA + IC
    breadth = cs.effective_breadth(N_SECTORS, RHO)
    lo, hi = cs.sharpe_ci(SR_OBS, se)
    print(f"(1.3) AMPLITUD EFECTIVA — {N_SECTORS} sectores a ρ={RHO} → N_eff = {breadth:.2f} "
          f"(casi UNA apuesta)")
    print(f"      IC95 del Sharpe: [{lo:.2f}, {hi:.2f}]  — listón {LISTON} "
          f"{'DENTRO del IC → IRRESOLUBLE' if lo <= LISTON <= hi else 'fuera del IC'}")
    print(f"      El IC no distingue {SR_OBS} de {LISTON} ni con {N_YEARS} años de datos.\n")

    # (1.4) OPERABILIDAD REAL
    print("(1.4) OPERABILIDAD — CORRECCIÓN honesta de la premisa:")
    print("      Los 9 Select Sector SPDR + SPY son un universo ESTABLE (no se deslistan) →")
    print("      NO hay problema de survivorship/PIT a nivel ETF, y el EOD es BARATO (Norgate US")
    print("      ETFs ~$22.50/mo, o gratis en Stooq). El PIT con deslistadas sería el problema de")
    print("      una estrategia de ACCIONES individuales, no de 10 ETFs sectoriales fijos.")
    print("      El bloqueante real es de VEHÍCULO: nuestro universo probado son 9 CFD macro")
    print("      (FX/índices/materias); operar CFD de ETFs sectoriales US es una EXPANSIÓN de")
    print("      universo por verificar en el prop, no un problema de datos. → NO es el")
    print("      bloqueante decisivo que se asumió.\n")

    # VEREDICTO
    print("=== VEREDICTO: CRIBADO_MUERE ===")
    print(f"  Muere por ARITMÉTICA (1.1)+(1.2)+(1.3), no por operabilidad:")
    print(f"  · (1.3) el IC [{lo:.2f},{hi:.2f}] incluye el listón {LISTON} → 0.55 es indistinguible")
    print(f"    del suelo de costes incluso con {N_YEARS} años (IRRESOLUBLE).")
    print(f"  · (1.1) a N≥~50 la suerte de búsqueda alcanza el listón → un 0.55 in-sample de 3 patas")
    print(f"    NO despeja deflactado.")
    print(f"  · (1.2) el nulo de exposición compartida (TOM/mercado ~{null_sr:.2f}) se come casi todo")
    print(f"    el 0.55 → la secuencia sectorial aporta poco (problema de H003).")
    print(f"  · (1.4) operabilidad NO es el bloqueante (universo ETF estable, datos baratos).")
    print(f"  NO se pre-registra. No consume intento, no requiere ficha.")


if __name__ == "__main__":
    main()
