# Corrección de procedencia + regla de figuras

## Por qué

La validación del extractor (`docs/extraction_validation.md`) destapó dos defectos en
NUESTRAS fichas manuales, no en el extractor — el conjunto de validación encontró errores en
el sistema que lo validaba, que es justo para lo que existe. Se corrigen SIN revisar
veredictos (H001/H007 congelados): como corrección de procedencia post-ejecución.

## Qué cambia

- **D1 — período de MOP** 1965-2009 → **1985-2009** (el paper reporta post-1985 como primario,
  §2.3 p.15/§4.1 p.16; 1965 era robustez). Corregido `periodo_original` en H001 (archive) y
  H007, y en `docs/program_verdict.md`.
- **D2 — Sharpe 1.2 sin cita** → `sharpe_reportado: null` + `sharpe_reportado_nota` (está en
  Figure 2, no en texto). En ambas fichas.
- **Forma:** las correcciones van como `tipo: correccion_procedencia_post_ejecucion` en el
  bloque `enmiendas` de cada ficha, con `afecta_veredicto: NO`, `afecta_expectativas_futuras:
  SÍ`. Las derivaciones congeladas conservan el 1.2/1965 histórico; la enmienda es el registro.
- **Regla nueva (c) — numéricos sólo en figuras** (`extract.py`): si un valor sólo está en una
  figura/gráfico, se emite null y se marca `requiere_lectura_manual: true`. Campo nuevo en el
  esquema; visible en el reporte de la compuerta humana; test que verifica null+flag (no valor
  inventado).
- **Registro de aprendizaje:** H001/H007 marcadas `ancla_defectuosa: 1`. El reporte recalcula
  el sesgo de calibración con y sin ellas y concluye **NO HAY CALIBRACIÓN TODAVÍA** (el +0.057
  previo no era evidencia limpia del marco Grinold-Kahn).
- **`docs/extraction_defects.md`:** los 4 defectos con estado (D1/D2 corregidos, D3 compuerta
  humana, D4 eje del adversario) + **nota de honestidad**: extractor y adversario fueron el
  MISMO modelo con ejes que YA conocíamos; no está demostrado que detecte un fallo NO
  anticipado. **Mitigación comprometida:** los primeros 20 candidatos de la corrida real se
  leen íntegros aunque el adversario diga KEEP.

## Impacto

- Fichas H001/H007, docs (program_verdict, extraction_defects), esquema (`requiere_lectura_manual`,
  `ancla_defectuosa`), extract.py/human_gate/learning_report + tests. Veredictos NO cambian.
  Suite 189 verde (+1 skip). NO se cablea API, NO se corre estación 1. Sin delta de spec.
