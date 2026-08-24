# Tareas

## 1. Gitignore
- [x] 1.1 Excluir `data/papers/*.pdf`/`*.PDF`; versionar README.md y MANIFEST.md.
- [x] 1.2 Auditar `git ls-files`: ningún PDF con copyright trackeado (los 3 estaban untracked).

## 2. README de procedencia
- [x] 2.1 `data/papers/README.md`: por qué no están en el repo, cómo obtenerlos, convención de
  nombre `{primer_autor}{año}_{palabra_clave}.pdf`, MANIFEST = fuente de verdad.

## 3. Manifiesto
- [x] 3.1 `data/papers/MANIFEST.md` versionado, una entrada por paper con SHA256/usado-en/estado.
- [x] 3.2 Precargar Moskowitz2012, ContKukanov2011, McConnell2008 (presentes, renombrados a la
  convención) + Ariel1987 (pendiente). El OFI ya estaba en el repo → movido con la convención.

## 4. Script de verificación
- [x] 4.1 `scripts/verify_papers.py`: presentes/ausentes, SHA256, aviso si falta hash, FALLA si
  no cuadra o si hay un PDF trackeado en git. Mismo patrón que raw/raw_crypto.

## 5. Loader mínimo
- [x] 5.1 `src/pipeline/papers.py::resolve_paper(id)` → ruta al PDF, fallo VISIBLE si ausente o
  id desconocido (disciplina DUKASCOPY_SYMBOLS). NO extracción, NO LLM.
- [x] 5.2 Tests (parseo de manifiesto, resolución presente/ausente/desconocido). Suite 182 verde.
