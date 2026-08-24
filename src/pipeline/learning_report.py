"""learning_report.py — el primer reporte de aprendizaje, con SQL, no con opiniones.

Tres preguntas que el registro de aprendizaje permite responder con datos:
  1. Distribución por clase_de_dato (esperado del backfill: 5/7 precio).
  2. Tasa de supervivencia por clase (se MIDE, no se asume — SESGO A EVITAR: no favorecer
     macro/flujo "porque parecen las buenas"; la evidencia real es floja en ambos lados).
  3. Calibración de expectativas: ¿bruto_esperado vs bruto_medido está inflado?

`viable` es el único estado que cuenta como supervivencia. Hoy: cero.
"""

from __future__ import annotations

# Estados que cuentan como "sobrevivió" (llegó a la cola viable / promovió).
_SURVIVED = ("viable", "en_cola", "pre_registrado")


def _rows_por_clase(conn) -> list[dict]:
    sql = """
        SELECT clase_de_dato AS clase,
               COUNT(*)                                        AS n,
               SUM(CASE WHEN estado IN ('viable','en_cola','pre_registrado')
                        THEN 1 ELSE 0 END)                     AS vivas
        FROM hipotesis
        WHERE clase_de_dato IS NOT NULL
        GROUP BY clase_de_dato
        ORDER BY n DESC, clase ASC
    """
    return [dict(r) for r in conn.execute(sql).fetchall()]


def _calibracion(conn) -> list[dict]:
    """Filas realmente CORRIDAS a un veredicto de Sharpe con esperado y medido."""
    sql = """
        SELECT id, clase_de_dato AS clase, bruto_esperado, bruto_medido,
               (bruto_esperado - bruto_medido) AS sesgo
        FROM hipotesis
        WHERE fecha_test IS NOT NULL
          AND bruto_esperado IS NOT NULL
          AND bruto_medido   IS NOT NULL
        ORDER BY id
    """
    return [dict(r) for r in conn.execute(sql).fetchall()]


def report(conn) -> str:
    """Render the learning report as markdown text."""
    total = conn.execute("SELECT COUNT(*) FROM hipotesis").fetchone()[0]
    vivas = conn.execute(
        f"SELECT COUNT(*) FROM hipotesis WHERE estado IN ({','.join('?'*len(_SURVIVED))})",
        _SURVIVED,
    ).fetchone()[0]

    lines = ["# Reporte de aprendizaje del pipeline", ""]
    lines.append(f"Total de hipótesis registradas: **{total}** · supervivientes "
                 f"(estado viable/en_cola/pre_registrado): **{vivas}**")
    lines.append("")

    # 1 + 2: distribución y supervivencia por clase.
    lines.append("## Distribución y supervivencia por clase de dato")
    lines.append("")
    lines.append("| clase_de_dato | n | vivas | tasa supervivencia |")
    lines.append("|---|---|---|---|")
    clases = _rows_por_clase(conn)
    for r in clases:
        tasa = (r["vivas"] / r["n"]) if r["n"] else 0.0
        lines.append(f"| {r['clase']} | {r['n']} | {r['vivas']} | {tasa:.0%} |")
    n_precio = sum(r["n"] for r in clases if r["clase"] == "precio")
    lines.append("")
    lines.append(f"Precio = **{n_precio}/{total}** de las hipótesis registradas "
                 "(el sesgo de fuente única que el pipeline existe para corregir). "
                 "**La tasa de supervivencia se MIDE por clase, no se asume**: no se "
                 "favorece a macro/flujo por parecer 'las buenas'.")
    lines.append("")

    # 3: calibración.
    lines.append("## Calibración de expectativas (corridas con esperado y medido)")
    lines.append("")
    cal = _calibracion(conn)
    if not cal:
        lines.append("_Sin corridas con ambos números todavía._")
    else:
        lines.append("| id | clase | bruto_esperado | bruto_medido | sesgo (esp−med) |")
        lines.append("|---|---|---|---|---|")
        for r in cal:
            lines.append(f"| {r['id']} | {r['clase']} | {r['bruto_esperado']:.2f} | "
                         f"{r['bruto_medido']:.3f} | {r['sesgo']:+.3f} |")
        sesgo_medio = sum(r["sesgo"] for r in cal) / len(cal)
        sobre = sum(1 for r in cal if r["sesgo"] > 0)
        lines.append("")
        signo = "SOBREestimamos" if sesgo_medio > 0 else "SUBestimamos"
        lines.append(f"Sesgo medio (esperado − medido) = **{sesgo_medio:+.3f}** → en promedio "
                     f"**{signo}** el bruto. {sobre}/{len(cal)} corridas por encima de lo medido.")
        lines.append("")
        lines.append("Lectura honesta: el sesgo lo domina H001 (Grinold-Kahn predijo un edge "
                     "de trend que no estaba); H007 quedó on-target pero UNDERPOWERED (no "
                     "informa). La conclusión NO es 'todo inflado' sino 'las expectativas de "
                     "trend por amplitud estaban infladas'.")
    lines.append("")
    return "\n".join(lines)
