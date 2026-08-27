"""pipeline.py — runner CLI del pipeline de investigación (estaciones 1-3).

Uso:
    python -m scripts.pipeline init                 # crea el esquema
    python -m scripts.pipeline backfill             # carga las 7 hipótesis conocidas
    python -m scripts.pipeline discover [--max N]   # estación 1 (cron MENSUAL)
    python -m scripts.pipeline triage               # estaciones 2 y 3 sobre candidatos
    python -m scripts.pipeline report               # reporte de aprendizaje
    python -m scripts.pipeline queue                # la siguiente hipótesis en cola

La opción --db apunta a otra base (por defecto data/pipeline/research.db).

NOTA de scheduling: `discover` está pensado para un cron MENSUAL del entorno
(el throughput real es ~una hipótesis al mes; un cron diario fabrica inventario muerto).
Ejemplo de crontab: `0 6 1 * *  cd <repo> && .venv/bin/python -m scripts.pipeline discover`.
"""

from __future__ import annotations

import argparse

from src.pipeline import backfill, db, discover, estimate, learning_report
from src.pipeline import triage_costs, triage_operability


def cmd_init(conn, args):
    db.init_db(conn)
    print("esquema creado (o ya existía).")


def cmd_backfill(conn, args):
    n = backfill.load_backfill(conn)
    print(f"backfill cargado: {n} hipótesis.")


def cmd_discover(conn, args):
    db.init_db(conn)
    counts = discover.discover(conn, max_results=args.max, include_rss=not args.no_rss)
    for src, n in counts.items():
        estado = "FALLÓ" if n < 0 else f"{n} nuevos"
        print(f"  {src:16s} {estado}")


def cmd_triage(conn, args):
    db.init_db(conn)
    candidatos = [r for r in db.all_rows(conn) if r["estado"] == "candidato"]
    print(f"triando {len(candidatos)} candidatos...")
    for c in candidatos:
        op = triage_operability.apply(conn, c["id"], c)
        if op.decision == "reject":
            print(f"  {c['id']:24s} OP reject — {op.razon}")
            continue
        # E2.5: estimar de forma DETERMINISTA los campos que el triaje de costos necesita
        # (frecuencia, duty, bruto reportado si está en el abstract). Sin esto, arXiv no se
        # puede cost-triar (los campos vienen vacíos). Ver src/pipeline/estimate.py.
        est = estimate.estimate_fields(c)
        db.upsert(conn, {"id": c["id"], **est})
        row = db.get(conn, c["id"])
        co = triage_costs.apply(conn, c["id"], row)
        # prioridad determinista (para ordenar el procesamiento en sesión)
        row = db.get(conn, c["id"])
        db.upsert(conn, {"id": c["id"], "score_prioridad": estimate.priority_score(row)})
        print(f"  {c['id']:24s} OP keep · COSTO {co.decision} — {co.razon}")


def cmd_report(conn, args):
    print(learning_report.report(conn))


def cmd_queue(conn, args):
    nxt = db.next_in_queue(conn)
    if nxt is None:
        print("cola vacía (ninguna hipótesis en estado 'en_cola').")
    else:
        print(f"siguiente: {nxt['id']} — {nxt['titulo']} (score {nxt.get('score_prioridad')})")


def main(argv=None):
    p = argparse.ArgumentParser(description="Pipeline de investigación PropLab (estaciones 1-3)")
    p.add_argument("--db", default=str(db.DEFAULT_DB_PATH), help="ruta a la base SQLite")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init").set_defaults(fn=cmd_init)
    sub.add_parser("backfill").set_defaults(fn=cmd_backfill)
    d = sub.add_parser("discover")
    d.add_argument("--max", type=int, default=50)
    d.add_argument("--no-rss", action="store_true")
    d.set_defaults(fn=cmd_discover)
    sub.add_parser("triage").set_defaults(fn=cmd_triage)
    sub.add_parser("report").set_defaults(fn=cmd_report)
    sub.add_parser("queue").set_defaults(fn=cmd_queue)

    args = p.parse_args(argv)
    conn = db.connect(args.db)
    try:
        args.fn(conn, args)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
