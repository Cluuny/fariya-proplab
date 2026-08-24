# Tareas

## 1. D1 — período de MOP
- [x] 1.1 `periodo_original` 1965-2009 → 1985-2009 en H001 (archive) y H007.
- [x] 1.2 Nota en `docs/program_verdict.md` (conclusión 7 / calibración).

## 2. D2 — Sharpe sin cita
- [x] 2.1 `sharpe_reportado: 1.2` → null + `sharpe_reportado_nota` (Figure 2) en ambas fichas.

## 3. Forma — corrección post-ejecución
- [x] 3.1 Enmienda `correccion_procedencia_post_ejecucion` en H001 y H007 (afecta_veredicto NO,
  afecta_expectativas_futuras SÍ, detalle del ancla). Derivaciones congeladas intactas.
- [x] 3.2 Misma nota en program_verdict (calibración de expectativas).

## 4. Regla nueva de figuras
- [x] 4.1 Campo `requiere_lectura_manual` en el esquema (db.py).
- [x] 4.2 Regla (c) explícita en el prompt/doc de la estación 4 (extract.py); se marca al caer
  un numérico sin cita.
- [x] 4.3 Campo visible en el reporte de la compuerta humana (human_gate).
- [x] 4.4 Test: numérico-sólo-en-figura → null + flag, no valor inventado.

## 5. Registro de aprendizaje
- [x] 5.1 Campo `ancla_defectuosa`; H001/H007 marcadas en el backfill.
- [x] 5.2 Reporte recalcula sesgo con y sin ancla defectuosa; concluye NO HAY CALIBRACIÓN TODAVÍA.

## 6. extraction_defects.md
- [x] 6.1 Los 4 defectos con estado (D1/D2 corregidos + regla c; D3 compuerta; D4 adversario).
- [x] 6.2 Nota de honestidad (mismo modelo, ejes conocidos) + mitigación (primeros 20 íntegros).
