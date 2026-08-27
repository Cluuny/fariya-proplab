"""e3_retro.py — retro-test de la recalibración de E3 sobre los candidatos YA procesados.

Aplica las reglas NUEVAS (factor de degradación 0.35, métricas alternativas para estimar el bruto,
familia_de_riesgo) a los candidatos de las corridas 001-002 y reporta qué habría cambiado, ANTES de
gastar corridas nuevas. NO toca la red: lee los volcados JSON de las corridas.

Uso:  python -m scripts.e3_retro run001.json run002.json
"""

from __future__ import annotations

import json
import sys
from collections import Counter

from src.pipeline import estimate, triage_costs, triage_operability


def _load(paths):
    filas = []
    for p in paths:
        with open(p) as fh:
            d = json.load(fh)
        for f in d.get("filas", []):
            filas.append({"id": f["id"], "titulo": f.get("titulo") or "",
                          "abstract": f.get("abstract") or "", "muerte_vieja": f.get("muerte"),
                          "triage_viejo": f.get("triage_costo")})
    return filas


def main(argv):
    filas = _load(argv)
    print(f"=== Retro-test de E3 sobre {len(filas)} candidatos procesados (runs 001-002) ===\n")

    e3_reject_nuevo = []      # mueren en E3 con el factor de degradación
    rescatados = []           # requiere_lectura → ahora con bruto (métrica alternativa)
    survivors = []            # llegan a en_cola/requiere_lectura tras E3
    fam_counter = Counter()

    for f in filas:
        op = triage_operability.triage_operability(f)
        if op.decision == "reject":
            continue
        es, _ = estimate.is_operable_strategy(f)
        if not es:
            continue
        est = estimate.estimate_fields(f)
        row = {**f, **est}
        co = triage_costs.triage_costs(row)
        if co.decision == "reject":
            e3_reject_nuevo.append((f["id"], est.get("bruto_reportado"), est.get("cita_bruto"), co.razon))
        else:
            survivors.append((f["id"], co.decision, est.get("bruto_reportado"), est.get("familia_de_riesgo")))
            fam_counter[est.get("familia_de_riesgo")] += 1
        # ¿lo rescató una métrica alternativa? (bruto por vía != "Sharpe" directo)
        cita = est.get("cita_bruto") or ""
        if est.get("bruto_reportado") is not None and ("→" in cita or "information ratio" in cita):
            rescatados.append((f["id"], est.get("bruto_reportado"), cita))

    print(f"(A) MÉTRICAS ALTERNATIVAS — rescatados de requiere_lectura: {len(rescatados)}")
    for i, b, c in rescatados:
        print(f"    {i[:34]:34s} bruto≈{b}  ({c})")
    if not rescatados:
        print("    (ninguno; los abstracts no traen ret/vol, IR ni t-stat extraíbles)")

    print(f"\n(B) FACTOR DE DEGRADACIÓN — mueren en E3 con la regla nueva: {len(e3_reject_nuevo)}")
    for i, b, c, r in e3_reject_nuevo:
        print(f"    {i[:40]:40s} reportado={b}  → {r[:70]}")

    print(f"\n(C) SUPERVIVIENTES de E3 tras la recalibración: {len(survivors)}")
    for i, dec, b, fam in survivors:
        print(f"    {i[:40]:40s} {dec:16s} bruto={b} familia={fam}")

    print(f"\n(D) DISTRIBUCIÓN por familia_de_riesgo de los supervivientes:")
    for fam, n in fam_counter.most_common():
        print(f"    {fam:16s} {n}")

    print(f"\n(E) TRABAJO DE SESIÓN AHORRADO: los que mueren en E3 ya no requieren lectura de sesión.")
    print(f"    E3 ahora decide {len(e3_reject_nuevo)} rechazos deterministas (antes: 0 en ambas corridas).")


if __name__ == "__main__":
    main(sys.argv[1:])
