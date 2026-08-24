# Preparar data/papers/ para la validación de extracción

## Por qué

La estación 4 del pipeline (extracción PDF→ficha) necesita un corpus de papers reproducible.
El repo es PÚBLICO y los papers tienen copyright → los PDFs no pueden commitearse. Hace falta
el mismo patrón que `data/raw`/`data/raw_crypto`: manifiesto versionado, binarios no. Solo
scaffolding — no se procesa ningún paper todavía.

## Qué cambia

- **.gitignore**: excluye `data/papers/*.pdf`/`*.PDF`, versiona `README.md` y `MANIFEST.md`.
  Auditado: **ningún PDF con copyright estaba trackeado** (los 3 presentes estaban untracked;
  el único PDF en git es el propio `PropLab_Documento_Maestro.pdf`, documento del proyecto).
- **data/papers/README.md**: procedencia (por qué no están en el repo), cómo obtenerlos
  (Scholar título exacto + filetype:pdf; AQR para Moskowitz/Pedersen; arXiv), convención de
  nombre `{primer_autor}{año}_{palabra_clave}.pdf`, y que MANIFEST es la fuente de verdad.
- **data/papers/MANIFEST.md** (versionado): 4 entradas con título/autores/DOI/URL/fecha/SHA256/
  usado-en/estado. Los 3 precargados que ya estaban en el repo, renombrados a la convención y
  con estado `presente`: moskowitz2012_tsmom (H001/H007), contkukanov2011_ofi (OFI),
  mcconnell2008_tom (H003); + ariel1987_tom como `pendiente` (demuestra el estado ausente).
- **scripts/verify_papers.py**: lista presentes/ausentes, verifica SHA256, avisa si falta
  registrar un hash, FALLA si un checksum no cuadra o si detecta un PDF trackeado en git.
- **src/pipeline/papers.py**: loader `resolve_paper(id)` → ruta al PDF, fallando VISIBLEMENTE
  si el id no está en el manifiesto o el PDF no está presente (disciplina DUKASCOPY_SYMBOLS,
  sin fallback silencioso).

## Impacto

- Scaffolding + tests. NO extracción, NO LLM (eso es pipeline-llm-live). Los PDFs siguen
  fuera del repo. Suite 182 verde. Sin delta de spec.
