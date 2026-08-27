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


def _rows_por_frecuencia(conn) -> list[dict]:
    sql = """
        SELECT COALESCE(frecuencia, 'EOD') AS frecuencia,
               COUNT(*) AS n,
               SUM(CASE WHEN estado IN ('viable','en_cola','pre_registrado')
                        THEN 1 ELSE 0 END) AS vivas
        FROM hipotesis
        GROUP BY COALESCE(frecuencia, 'EOD')
        ORDER BY n DESC, frecuencia ASC
    """
    return [dict(r) for r in conn.execute(sql).fetchall()]


def _rows_por_tipo_fuente(conn) -> list[dict]:
    sql = """
        SELECT tipo_de_fuente AS tipo, COUNT(*) AS n,
               SUM(CASE WHEN estado IN ('viable','en_cola','pre_registrado')
                        THEN 1 ELSE 0 END) AS vivas
        FROM hipotesis WHERE tipo_de_fuente IS NOT NULL
        GROUP BY tipo_de_fuente ORDER BY n DESC, tipo ASC
    """
    return [dict(r) for r in conn.execute(sql).fetchall()]


# Estados de rechazo ANTERIORES o EN el eje es_estrategia_operable (no pasaron el eje).
_PRE_O_EN_EJE_ESTRATEGIA = (
    "candidato", "rechazada_operabilidad", "rechazada_por_falsabilidad",
    "rechazada_por_datos", "rechazada_no_estrategia",
)


def _densidad_estrategia_por_fuente(conn) -> list[dict]:
    """DENSIDAD DE ESTRATEGIAS OPERABLES POR FUENTE = pasan es_estrategia_operable / descubiertos.

    El número que dice DÓNDE BUSCAR. `descubiertos` = filas procesadas (estado != 'candidato')
    de esa fuente; `pasan_eje` = las que superaron el eje es_estrategia_operable (estado no está
    entre los rechazos anteriores o en el propio eje). Se reporta por `fuente` en cada corrida."""
    placeholders = ",".join("?" * len(_PRE_O_EN_EJE_ESTRATEGIA))
    sql = f"""
        SELECT fuente,
               SUM(CASE WHEN estado != 'candidato' THEN 1 ELSE 0 END) AS descubiertos,
               SUM(CASE WHEN estado NOT IN ({placeholders}) THEN 1 ELSE 0 END) AS pasan_eje
        FROM hipotesis
        WHERE fuente IS NOT NULL
        GROUP BY fuente
        HAVING descubiertos > 0
        ORDER BY pasan_eje * 1.0 / descubiertos DESC, descubiertos DESC
    """
    return [dict(r) for r in conn.execute(sql, _PRE_O_EN_EJE_ESTRATEGIA).fetchall()]


def _por_familia_riesgo(conn) -> list[dict]:
    """Supervivientes por familia_de_riesgo. Si los CUATRO que hacen falta salen de la misma
    familia, no hay diversificación y el 0.4·√4=0.8 NO se alcanza (change e3-recalibration)."""
    sql = """
        SELECT COALESCE(familia_de_riesgo, 'sin_clasificar') AS familia,
               COUNT(*) AS n,
               SUM(CASE WHEN estado IN ('viable','en_cola','pre_registrado') THEN 1 ELSE 0 END) AS vivas
        FROM hipotesis
        WHERE estado != 'candidato'
        GROUP BY COALESCE(familia_de_riesgo, 'sin_clasificar')
        ORDER BY vivas DESC, n DESC
    """
    return [dict(r) for r in conn.execute(sql).fetchall()]


def _calibracion(conn) -> list[dict]:
    """Filas realmente CORRIDAS a un veredicto de Sharpe con esperado y medido."""
    sql = """
        SELECT id, clase_de_dato AS clase, bruto_esperado, bruto_medido,
               (bruto_esperado - bruto_medido) AS sesgo,
               COALESCE(ancla_defectuosa, 0) AS ancla_defectuosa
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

    from src.pipeline import db

    procesados = db.count_processed(conn)
    lines = ["# Reporte de aprendizaje del pipeline", ""]
    lines.append(f"**Condición de parada: {procesados} / {db.N_CONDICION_PARADA} candidatos "
                 f"procesados.** (docs/pipeline_stop_condition.md)")
    lines.append(f"Total registradas: **{total}** · supervivientes "
                 f"(viable/en_cola/pre_registrado): **{vivas}**")
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

    # distribución por frecuencia (intradía vs EOD).
    lines.append("## Distribución por frecuencia")
    lines.append("")
    lines.append("| frecuencia | n | vivas |")
    lines.append("|---|---|---|")
    for r in _rows_por_frecuencia(conn):
        lines.append(f"| {r['frecuencia']} | {r['n']} | {r['vivas']} |")
    lines.append("")

    # distribución + supervivencia por tipo de fuente (¿producen las no académicas algo testeable?)
    lines.append("## Distribución y supervivencia por tipo de fuente")
    lines.append("")
    lines.append("| tipo_de_fuente | n | vivas | rechazadas | tasa rechazo |")
    lines.append("|---|---|---|---|---|")
    for r in _rows_por_tipo_fuente(conn):
        rej = r["n"] - r["vivas"]
        lines.append(f"| {r['tipo']} | {r['n']} | {r['vivas']} | {rej} | {(rej/r['n']) if r['n'] else 0:.0%} |")
    lines.append("")
    lines.append("La tasa de rechazo por tipo de fuente es un RESULTADO: dice si las fuentes "
                 "no académicas (reddit/twitter/discord/youtube) producen algo testeable o sólo "
                 "contenido. Todas pasan por los mismos filtros.")
    lines.append("")

    # DENSIDAD DE ESTRATEGIAS OPERABLES POR FUENTE (el número que dice dónde buscar).
    dens = _densidad_estrategia_por_fuente(conn)
    if dens:
        lines.append("## Densidad de estrategias operables por fuente")
        lines.append("")
        lines.append("| fuente | descubiertos | pasan es_estrategia_operable | densidad |")
        lines.append("|---|---|---|---|")
        for r in dens:
            de, pa = r["descubiertos"], r["pasan_eje"]
            lines.append(f"| {r['fuente']} | {de} | {pa} | {(pa/de) if de else 0:.0%} |")
        lines.append("")
        lines.append("**Densidad = pasan es_estrategia_operable / descubiertos.** Es el número que "
                     "dice DÓNDE BUSCAR: una fuente de estrategias destiladas (Quantpedia) debería "
                     "densificar más que un repositorio de metodología (arXiv). Se mide, no se asume.")
        lines.append("")

    # supervivientes por FAMILIA DE RIESGO (¿hay diversificación para el 0.4·√4=0.8?)
    fam = _por_familia_riesgo(conn)
    if fam:
        lines.append("## Supervivientes por familia de riesgo")
        lines.append("")
        lines.append("| familia_de_riesgo | procesados | vivas |")
        lines.append("|---|---|---|")
        for r in fam:
            lines.append(f"| {r['familia']} | {r['n']} | {r['vivas']} |")
        lines.append("")
        lines.append("**El objetivo son CUATRO estrategias DESCORRELACIONADAS (0.4·√4 = 0.8).** Si los "
                     "cuatro supervivientes salieran de la MISMA familia, no habría diversificación y el "
                     "0.8 no se alcanza. La diversificación se MIDE aquí, no se asume.")
        lines.append("")

    # causa de muerte
    lines.append("## Causa de muerte")
    lines.append("")
    lines.append("| causa | n |")
    lines.append("|---|---|")
    for causa, n in conn.execute(
        "SELECT causa_de_muerte, COUNT(*) FROM hipotesis WHERE causa_de_muerte IS NOT NULL "
        "GROUP BY causa_de_muerte ORDER BY COUNT(*) DESC").fetchall():
        lines.append(f"| {causa} | {n} |")
    lines.append("")

    # EL TEST del pipeline: ¿sobreviven más las ideas del pipeline que las del reviewer?
    lines.append("## ¿Vale la pena el pipeline? (supervivencia pipeline vs reviewer)")
    lines.append("")
    lines.append("| fuente_de_la_idea | n | vivas | tasa supervivencia |")
    lines.append("|---|---|---|---|")
    for fte, n, v in conn.execute(
        "SELECT fuente_de_la_idea, COUNT(*), "
        "SUM(CASE WHEN estado IN ('viable','en_cola','pre_registrado') THEN 1 ELSE 0 END) "
        "FROM hipotesis WHERE fuente_de_la_idea IS NOT NULL GROUP BY fuente_de_la_idea").fetchall():
        lines.append(f"| {fte} | {n} | {v} | {(v/n) if n else 0:.0%} |")
    lines.append("")
    lines.append("**Éste es el test de si el pipeline valió la pena:** que las ideas del "
                 "pipeline sobrevivan MÁS que las del reviewer. Hoy sólo hay reviewer (backfill); "
                 "el número se llena cuando el pipeline produzca candidatos.")
    lines.append("")

    # SESGO A EVITAR (registrado explícitamente)
    lines.append("> SESGO A EVITAR: no se favorece a macro/fundamentales/volatilidad 'porque "
                 "parecen las buenas'. La evidencia es 1 de 2 (carry acertó con 0.282, COT dio "
                 "cero exacto). La supervivencia por clase se MIDE, no se asume.")
    lines.append("")

    # 3: calibración.
    lines.append("## Calibración de expectativas (corridas con esperado y medido)")
    lines.append("")
    cal = _calibracion(conn)
    if not cal:
        lines.append("_Sin corridas con ambos números todavía._")
    else:
        lines.append("| id | clase | bruto_esperado | bruto_medido | sesgo (esp−med) | ancla |")
        lines.append("|---|---|---|---|---|---|")
        for r in cal:
            ancla = "DEFECTUOSA" if r["ancla_defectuosa"] else "ok"
            lines.append(f"| {r['id']} | {r['clase']} | {r['bruto_esperado']:.2f} | "
                         f"{r['bruto_medido']:.3f} | {r['sesgo']:+.3f} | {ancla} |")
        sesgo_todos = sum(r["sesgo"] for r in cal) / len(cal)
        limpias = [r for r in cal if not r["ancla_defectuosa"]]
        sesgo_limpio = (sum(r["sesgo"] for r in limpias) / len(limpias)) if limpias else None
        lines.append("")
        lines.append(f"Sesgo medio con TODAS ({len(cal)}): **{sesgo_todos:+.3f}**. "
                     f"Con ancla limpia ({len(limpias)}): "
                     f"{('**%+.3f**' % sesgo_limpio) if sesgo_limpio is not None else '**n/a**'}.")
        lines.append("")
        n_def = sum(1 for r in cal if r["ancla_defectuosa"])
        lines.append(f"**NO HAY CALIBRACIÓN TODAVÍA.** De {len(cal)} puntos, {n_def} tienen "
                     "**ancla defectuosa** (bruto_esperado derivado del 1.2 de MOP mal citado, "
                     "D2 en docs/extraction_defects.md), y el único de ancla limpia (H003) es "
                     "una expectativa de beta/estacionalidad, no un ancla Grinold-Kahn de trend. "
                     "Con ≤1 punto limpio no se puede afirmar que el marco sobre/subestime: el "
                     "+0.057 previo NO era evidencia limpia. La calibración empieza a existir "
                     "cuando el pipeline produzca corridas con ancla citable.")
    lines.append("")
    return "\n".join(lines)
