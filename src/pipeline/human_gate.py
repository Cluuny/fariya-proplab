"""human_gate.py — Estación 7: compuerta humana.

15 min/mes: se surfacean 3-5 candidatos (los que pasaron triajes + revisión adversaria),
ordenados por prioridad, y el humano aprueba UNO. El pipeline no auto-aprueba nada: la última
decisión es humana y barata en tiempo.
"""

from __future__ import annotations


def candidates_for_review(conn, *, limit: int = 5) -> list[dict]:
    """Los candidatos listos para la compuerta: en cola, que pasaron la revisión adversaria
    (o aún sin ella), ordenados por prioridad. Máx `limit` (3-5)."""
    sql = """
        SELECT * FROM hipotesis
        WHERE estado = 'en_cola'
          AND (adversarial_veredicto IS NULL OR adversarial_veredicto = 'keep')
        ORDER BY score_prioridad DESC NULLS LAST, id ASC
        LIMIT ?
    """
    return [dict(r) for r in conn.execute(sql, (limit,)).fetchall()]


def approve(conn, hyp_id: str) -> None:
    """Aprueba UNO → pre_registrado (listo para stub + implementación)."""
    from src.pipeline import db

    row = db.get(conn, hyp_id)
    if row is None:
        raise KeyError(hyp_id)
    if row["estado"] != "en_cola":
        raise ValueError(f"{hyp_id} no está en_cola (estado={row['estado']})")
    db.upsert(conn, {"id": hyp_id, "estado": "pre_registrado"})


def render(candidates: list[dict]) -> str:
    if not candidates:
        return "Compuerta humana: no hay candidatos listos para revisión."
    lines = [f"Compuerta humana — {len(candidates)} candidato(s), aprobar UNO:", ""]
    for i, c in enumerate(candidates, 1):
        manual = "  ⚠ requiere_lectura_manual (numérico sólo en figura)" if c.get("requiere_lectura_manual") else ""
        lines.append(f"{i}. {c['id']} — {c.get('titulo','')} "
                     f"[{c.get('clase_de_dato','?')} · {c.get('tipo_de_fuente','?')} · "
                     f"bruto {c.get('bruto_reportado','?')}]{manual}")
    return "\n".join(lines)
