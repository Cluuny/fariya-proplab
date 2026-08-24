# Conectar y validar el LLM del pipeline (estaciones 4-5)

## Por qué

Las estaciones 4 (extracción) y 5 (revisión adversaria) tenían la lógica construida y testeada
pero la llamada al modelo era un seam sin implementar; el pipeline nunca había procesado un
paper real. Antes de sacar una API key y automatizar, hay que validar la CALIDAD de la
extracción contra casos conocidos. Si produce basura, nos ahorramos el trámite.

## Qué cambia

- **Diagnóstico** del seam (extract.py:70, adversarial.py:37) y de los tests (no usaban LLM).
- **Extracción en sesión** (validación manual asistida): leí los 3 papers presentes
  (moskowitz2012_tsmom, mcconnell2008_tom, contkukanov2011_ofi) y produje fichas respetando las
  dos reglas anti-alucinación. `scripts/extraction_validation.py` corre esas fichas por las
  estaciones 4-5 REALES.
- **Validación contra casos conocidos** (`docs/extraction_validation.md`): tabla campo por
  campo vs H001/H007 y H003, y vs el propio paper para OFI. El adversario rechaza
  independientemente TOM (beta) y OFI (contemporáneo) — las dos familias que murieron por eso.
- **Defectos** (`docs/extraction_defects.md`): la validación destapó defectos de NUESTRAS
  fichas manuales, no del extractor — D1 período MOP 1965 vs 1985-2009; D2 Sharpe 1.2 sin cita
  (está en Figure 2, el extractor lo dejó null por la regla a); D3 falsador-inútil (lo que el
  esquema no atrapa → compuerta humana); D4 benchmark de TOM = beta.
- **Seam listo para automatizar** (`src/pipeline/llm_client.py`, sin conectar): firma clara,
  credencial por `PIPELINE_LLM_API_KEY` (nunca en el repo), structured output obligatorio
  (valida o rechaza), log de cada llamada, reintento con backoff, fallo visible. Tests con
  fakes + un test de integración skip-si-no-hay-credencial.
- **Coste estimado**: ~30k in + 2k out por paper extraído; ~200 candidatos → ~$1-18 total según
  modelo (Haiku ~$1.2). Despreciable vs el presupuesto de datos $125/mes → la condición de
  parada (200) es alcanzable; el cuello es el DATO, no el LLM.

## Impacto

- Nuevo `src/pipeline/llm_client.py`, `scripts/extraction_validation.py`, docs, tests. NO se
  conecta ninguna API, NO se procesan papers nuevos, NO se corre la estación 1 sobre arXiv (eso
  es el change siguiente, con API key). Suite 188 verde (+1 skip). Sin delta de spec.
