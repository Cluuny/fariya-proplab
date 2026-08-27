"""pipeline_run_002.py — segunda corrida (eje es_estrategia_operable + rebalanceo de fuentes).

Cambios vs 001:
  - DB PERSISTENTE (`data/pipeline/research.db`, gitignored) para que el contador ACUMULE.
    Se SIEMBRA la run 001 (desde su volcado JSON) para que el contador llegue a 91/200 de
    forma honesta (backfill 11 + run001 40 + run002 40).
  - E1 REBALANCEADO: arXiv con MENOR cuota; se sube el peso de RSS (Alpha Architect, CXO) y se
    añade **Quantpedia** (estrategias ya destiladas → mayor densidad esperada). SSRN no tiene
    API pública → ingesta manual (no se puede subir automáticamente; se anota).
  - DÉCIMO EJE `es_estrategia_operable` en E2.5 (determinista, antes del adversario): mata el
    modo dominante de la run 001 (método/teoría/modelo/monitor) barato.
  - MÉTRICA nueva: DENSIDAD de estrategias operables por fuente (= pasan el eje / descubiertos).

Uso:  python -m scripts.pipeline_run_002 [--arxiv-max 12] [--cap 40] [--seed run001.json] [--json out.json]
"""

from __future__ import annotations

import argparse
import json

from src.pipeline import backfill, db, discover, estimate, triage_costs, triage_operability

CAP_DEFAULT = 40
ARXIV_MAX_DEFAULT = 12   # cuota reducida de arXiv (run 001 fue ~95% arXiv, casi todo metodología)


def _estado_run001(fila: dict) -> dict:
    """Reconstruye el estado E1-E3 de una fila de la run 001 (para sembrar la DB persistente)."""
    if fila.get("estacion_muerte") == "E2":
        estado = {"falsabilidad": "rechazada_por_falsabilidad"}.get(
            fila.get("categoria"), "rechazada_operabilidad")
    else:
        estado = {"requiere_lectura": "requiere_lectura", "reject": "rechazada_costo",
                  "keep": "en_cola"}.get(fila.get("triage_costo"), "requiere_lectura")
    return {
        "id": fila["id"], "titulo": fila.get("titulo") or fila["id"], "abstract": fila.get("abstract"),
        "url": fila.get("url"), "fecha": fila.get("fecha"), "fuente": fila.get("fuente"),
        "tipo_de_fuente": fila.get("tipo_de_fuente"), "frecuencia": fila.get("frecuencia"),
        "clase_de_dato": fila.get("clase_de_dato"), "estado": estado,
    }


def seed_run001(conn, path: str) -> int:
    """Siembra las 40 filas de la run 001 (idempotente por id). Devuelve cuántas se escribieron."""
    with open(path) as fh:
        run001 = json.load(fh)
    written = 0
    for fila in run001.get("filas", []):
        if db.get(conn, fila["id"]) is None:
            db.upsert(conn, _estado_run001(fila))
            written += 1
    return written


def run(*, arxiv_max: int = ARXIV_MAX_DEFAULT, cap: int = CAP_DEFAULT, seed: str | None = None,
        db_path: str = str(db.DEFAULT_DB_PATH)) -> dict:
    conn = db.connect(db_path)
    db.init_db(conn)
    backfill.load_backfill(conn)
    seeded = seed_run001(conn, seed) if seed else 0

    # E1 rebalanceado: arXiv con cuota reducida; RSS (AA, CXO, Quantpedia) al peso completo.
    counts = discover.discover(conn, max_results=arxiv_max, include_rss=True)

    # REBALANCE: se procesan primero las fuentes NO-arXiv (RSS/Quantpedia, estrategias más
    # destiladas), y arXiv rellena hasta el cap → arXiv toma la CUOTA MENOR del set procesado.
    # (arXiv aporta profundidad, pero no domina el mix como en la run 001.)
    candidatos = [r for r in db.all_rows(conn) if r["estado"] == "candidato"]
    candidatos.sort(key=lambda r: (r.get("fuente") == "arxiv", _neg_fecha(r)))
    procesar = candidatos[:cap]

    funnel = {"descubiertos_nuevos": len(candidatos), "procesar": len(procesar),
              "E2_reject": 0, "E25_no_estrategia": 0,
              "E3_reject": 0, "E3_keep": 0, "E3_requiere_lectura": 0}
    por_fuente: dict[str, dict] = {}
    filas: list[dict] = []

    for c in procesar:
        fu = c.get("fuente") or "?"
        pf = por_fuente.setdefault(fu, {"descubiertos": 0, "pasan_eje": 0})
        pf["descubiertos"] += 1

        op = triage_operability.apply(conn, c["id"], c)
        if op.decision == "reject":
            funnel["E2_reject"] += 1
            filas.append({**_slim(c), "muerte": "E2", "razon": op.razon, "categoria": op.categoria})
            continue

        es_estrat, razon_es = estimate.is_operable_strategy(c)
        if not es_estrat:
            funnel["E25_no_estrategia"] += 1
            db.upsert(conn, {"id": c["id"], "estado": "rechazada_no_estrategia",
                             "causa_de_muerte": "no_estrategia", "triage_operabilidad_razon": razon_es})
            filas.append({**_slim(c), "muerte": "E2.5", "razon": razon_es})
            continue
        pf["pasan_eje"] += 1   # superó es_estrategia_operable

        est = estimate.estimate_fields(c)
        db.upsert(conn, {"id": c["id"], **est})
        row = db.get(conn, c["id"])
        co = triage_costs.apply(conn, c["id"], row)
        row = db.get(conn, c["id"])
        db.upsert(conn, {"id": c["id"], "score_prioridad": estimate.priority_score(row)})
        row = db.get(conn, c["id"])

        funnel[{"reject": "E3_reject", "keep": "E3_keep",
                "requiere_lectura": "E3_requiere_lectura"}[co.decision]] += 1
        filas.append({**_slim(row), "muerte": ("E3" if co.decision == "reject" else None),
                      "triage_costo": co.decision, "razon": co.razon,
                      "requerido_cfd": co.requerido_cfd, "requerido_intraday": co.requerido_intraday})

    survivors = [f for f in filas if f.get("triage_costo") in ("keep", "requiere_lectura")]
    survivors.sort(key=lambda f: (f.get("score_prioridad") or 0), reverse=True)

    # densidad por fuente (sólo las fuentes de descubrimiento de ESTA corrida)
    densidad = {fu: {"descubiertos": d["descubiertos"], "pasan_eje": d["pasan_eje"],
                     "densidad": (d["pasan_eje"] / d["descubiertos"]) if d["descubiertos"] else 0.0}
                for fu, d in por_fuente.items()}

    return {"discover_counts": counts, "seeded_run001": seeded, "funnel": funnel,
            "densidad_por_fuente": densidad, "filas": filas, "survivors": survivors,
            "counter": {"total": db.count_processed(conn), "N": db.N_CONDICION_PARADA}}


def _neg_fecha(r: dict) -> str:
    """Clave de orden por fecha DESC (más reciente primero) sin comparar contra None."""
    f = r.get("fecha") or ""
    return "".join(chr(255 - ord(c)) for c in f) if f else chr(255)


def _slim(r: dict) -> dict:
    keys = ("id", "titulo", "url", "fecha", "fuente", "tipo_de_fuente", "frecuencia",
            "clase_de_dato", "duty_cycle_estimado", "bruto_reportado", "cita_bruto",
            "score_prioridad", "abstract")
    return {k: r.get(k) for k in keys}


def main(argv=None):
    p = argparse.ArgumentParser(description="Segunda corrida del pipeline (E1-E3 + eje estrategia)")
    p.add_argument("--arxiv-max", type=int, default=ARXIV_MAX_DEFAULT)
    p.add_argument("--cap", type=int, default=CAP_DEFAULT)
    p.add_argument("--seed", default=None, help="volcado JSON de la run 001 para sembrar la DB")
    p.add_argument("--db", default=str(db.DEFAULT_DB_PATH))
    p.add_argument("--json", default=None)
    args = p.parse_args(argv)

    res = run(arxiv_max=args.arxiv_max, cap=args.cap, seed=args.seed, db_path=args.db)
    f = res["funnel"]
    print("=== E1 discover (rebalanceado) ===")
    for src, n in res["discover_counts"].items():
        print(f"  {src:22s} {'FALLÓ' if n < 0 else f'{n} nuevos'}")
    print(f"  (sembradas run001: {res['seeded_run001']})")
    print(f"\n=== EMBUDO (cap {args.cap}) ===")
    print(f"  descubiertos nuevos: {f['descubiertos_nuevos']} → procesar: {f['procesar']}")
    print(f"  E2 reject: {f['E2_reject']} · E2.5 no-estrategia: {f['E25_no_estrategia']}")
    print(f"  E3 reject: {f['E3_reject']} · keep: {f['E3_keep']} · requiere_lectura: {f['E3_requiere_lectura']}")
    print(f"\n=== DENSIDAD de estrategias operables por fuente ===")
    for fu, d in sorted(res["densidad_por_fuente"].items(), key=lambda kv: -kv[1]["densidad"]):
        print(f"  {fu:18s} {d['pasan_eje']}/{d['descubiertos']} = {d['densidad']:.0%}")
    print(f"\n=== SUPERVIVIENTES de E3 ({len(res['survivors'])}), por prioridad ===")
    for s in res["survivors"]:
        print(f"  [{s.get('score_prioridad')}] {s['id']} · {s.get('triage_costo')} · "
              f"{s.get('fuente')} · {s.get('titulo','')[:62]}")
    print(f"\n=== CONTADOR DE PARADA: {res['counter']['total']} / {res['counter']['N']} ===")
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(res, fh, ensure_ascii=False, indent=2)
        print(f"[volcado → {args.json}]")


if __name__ == "__main__":
    main()
