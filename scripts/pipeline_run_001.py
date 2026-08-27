"""pipeline_run_001.py — primera corrida real del pipeline (estaciones 1-3, batch).

Determinista salvo por la RED (E1). Reproducible en estructura: DB fresca en memoria,
backfill (11 conocidas), discover LIVE (arXiv q-fin PM/ST/TR + barrido microestructura +
RSS), CAP a 40 candidatos NUEVOS procesados por E1-E3 (no consume la cuota de parada de 200),
E2 (operabilidad) → E2.5 (estimación determinista) → E3 (costes) → prioridad.

E4-E5 (extracción + adversario) NO van aquí: se corren EN SESIÓN sobre los supervivientes.

Uso:  python -m scripts.pipeline_run_001 [--max 50] [--cap 40] [--json out.json]
"""

from __future__ import annotations

import argparse
import json

from src.pipeline import backfill, db, discover, estimate, triage_costs, triage_operability

CAP_DEFAULT = 40   # no consumir la cuota de parada (200) en la primera corrida


def run(*, max_results: int = 50, cap: int = CAP_DEFAULT) -> dict:
    conn = db.connect(":memory:")
    db.init_db(conn)
    n_backfill = backfill.load_backfill(conn)

    # E1 — descubrimiento (live). discover() es robusto a caída por fuente.
    counts = discover.discover(conn, max_results=max_results, include_rss=True)

    # CAP: procesar sólo los primeros `cap` candidatos NUEVOS (estado 'candidato'),
    # ordenados por fecha desc (los más recientes primero); el resto queda sin procesar.
    candidatos = [r for r in db.all_rows(conn) if r["estado"] == "candidato"]
    candidatos.sort(key=lambda r: (r.get("fecha") or ""), reverse=True)
    procesar = candidatos[:cap]

    funnel = {"E1_descubiertos": len(candidatos), "E1_cap": len(procesar),
              "E2_reject": 0, "E3_reject": 0, "E3_keep": 0, "E3_requiere_lectura": 0}
    por_fuente: dict[str, dict] = {}
    filas: list[dict] = []

    for c in procesar:
        tf = c.get("tipo_de_fuente") or "?"
        pf = por_fuente.setdefault(tf, {"n": 0, "rechazados": 0})
        pf["n"] += 1

        op = triage_operability.apply(conn, c["id"], c)
        if op.decision == "reject":
            funnel["E2_reject"] += 1
            pf["rechazados"] += 1
            filas.append({**_slim(c), "estacion_muerte": "E2", "razon": op.razon,
                          "categoria": op.categoria})
            continue

        # E2.5 — estimación determinista de los campos que E3 necesita
        est = estimate.estimate_fields(c)
        db.upsert(conn, {"id": c["id"], **est})
        row = db.get(conn, c["id"])

        co = triage_costs.apply(conn, c["id"], row)
        row = db.get(conn, c["id"])
        db.upsert(conn, {"id": c["id"], "score_prioridad": estimate.priority_score(row)})
        row = db.get(conn, c["id"])

        if co.decision == "reject":
            funnel["E3_reject"] += 1
            pf["rechazados"] += 1
        elif co.decision == "keep":
            funnel["E3_keep"] += 1
        else:
            funnel["E3_requiere_lectura"] += 1
        filas.append({**_slim(row), "estacion_muerte": ("E3" if co.decision == "reject" else None),
                      "triage_costo": co.decision, "razon": co.razon,
                      "requerido_cfd": co.requerido_cfd, "requerido_futuros": co.requerido_futuros,
                      "requerido_intraday": co.requerido_intraday})

    survivors = [f for f in filas if f.get("triage_costo") in ("keep", "requiere_lectura")]
    survivors.sort(key=lambda f: (f.get("score_prioridad") or 0), reverse=True)

    return {
        "discover_counts": counts,
        "funnel": funnel,
        "por_fuente": por_fuente,
        "filas": filas,
        "survivors": survivors,
        "counter_parada": {"backfill": n_backfill, "esta_corrida": len(procesar),
                           "total": db.count_processed(conn), "N": db.N_CONDICION_PARADA},
    }


def _slim(r: dict) -> dict:
    keys = ("id", "titulo", "url", "fecha", "fuente", "tipo_de_fuente", "frecuencia",
            "clase_de_dato", "duty_cycle_estimado", "turnover_estimado", "trades_por_dia_estimado",
            "contrato_ref", "bruto_reportado", "cita_bruto", "score_prioridad", "abstract")
    return {k: r.get(k) for k in keys}


def main(argv=None):
    p = argparse.ArgumentParser(description="Primera corrida del pipeline (E1-E3)")
    p.add_argument("--max", type=int, default=50)
    p.add_argument("--cap", type=int, default=CAP_DEFAULT)
    p.add_argument("--json", default=None, help="volcar el resultado completo a un JSON")
    args = p.parse_args(argv)

    res = run(max_results=args.max, cap=args.cap)
    f = res["funnel"]
    print("=== E1 discover (por fuente) ===")
    for src, n in res["discover_counts"].items():
        print(f"  {src:22s} {'FALLÓ' if n < 0 else f'{n} nuevos'}")
    print(f"\n=== EMBUDO (cap {args.cap}) ===")
    print(f"  E1 descubiertos: {f['E1_descubiertos']}  → procesados (cap): {f['E1_cap']}")
    print(f"  E2 reject: {f['E2_reject']}")
    print(f"  E3 reject: {f['E3_reject']} · keep: {f['E3_keep']} · requiere_lectura: {f['E3_requiere_lectura']}")
    print(f"\n=== por tipo de fuente ===")
    for tf, d in sorted(res["por_fuente"].items()):
        print(f"  {tf:16s} n={d['n']:3d} rechazados={d['rechazados']:3d} ({100*d['rechazados']/max(d['n'],1):.0f}%)")
    print(f"\n=== SUPERVIVIENTES de E3 ({len(res['survivors'])}), por prioridad ===")
    for s in res["survivors"]:
        print(f"  [{s.get('score_prioridad')}] {s['id']} · {s.get('triage_costo')} · "
              f"{s.get('frecuencia')} · bruto={s.get('bruto_reportado')} · {s.get('titulo','')[:70]}")
    c = res["counter_parada"]
    print(f"\n=== CONTADOR DE PARADA: {c['total']} / {c['N']} "
          f"(backfill {c['backfill']} + esta corrida {c['esta_corrida']}) ===")

    if args.json:
        with open(args.json, "w") as fh:
            json.dump(res, fh, ensure_ascii=False, indent=2)
        print(f"\n[volcado completo → {args.json}]")


if __name__ == "__main__":
    main()
