"""papers.py — loader del corpus de papers (data/papers/).

Resuelve un paper por su id del manifiesto y devuelve la ruta al PDF, fallando VISIBLEMENTE
si el archivo no está presente — misma disciplina que DUKASCOPY_SYMBOLS: si falta un mapeo,
error explícito, no fallback silencioso. NO extrae nada ni llama a ningún LLM (eso es el
change siguiente, pipeline-llm-live).

El MANIFEST (`data/papers/MANIFEST.md`) es la fuente de verdad: los PDFs no se versionan
(copyright + repo público).
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

PAPERS_DIR = Path("data/papers")
MANIFEST_PATH = PAPERS_DIR / "MANIFEST.md"
_CHUNK = 1 << 20


class PaperNotFoundError(FileNotFoundError):
    """El paper no está en el manifiesto, o está pero el PDF no está presente."""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(_CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def _paper_id(filename: str) -> str:
    return filename[:-4] if filename.lower().endswith(".pdf") else filename


def parse_manifest(path: Path = MANIFEST_PATH) -> dict[str, dict]:
    """Parse MANIFEST.md → {id: {filename, sha256, estado, ...campos}}. `id` = nombre del
    archivo sin `.pdf` (el encabezado `## <archivo>`)."""
    if not path.exists():
        raise FileNotFoundError(f"no existe el manifiesto de papers: {path}")
    entries: dict[str, dict] = {}
    current: dict | None = None
    for line in path.read_text().splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m and m.group(1).lower().endswith(".pdf"):
            fn = m.group(1).strip()
            current = {"filename": fn}
            entries[_paper_id(fn)] = current
            continue
        if current is not None:
            b = re.match(r"^\s*-\s*([^:]+):\s*(.*)$", line)
            if b:
                key = b.group(1).strip().lower()
                val = b.group(2).strip()
                if key == "sha256":
                    current["sha256"] = None if val in ("", "—", "-") else val.lower()
                elif key == "estado":
                    current["estado"] = val
                else:
                    current[key] = val
    return entries


def resolve_paper(paper_id: str, *, papers_dir: Path = PAPERS_DIR,
                  manifest: Path = MANIFEST_PATH) -> Path:
    """Devuelve la ruta al PDF de `paper_id`. Falla VISIBLEMENTE si el id no está en el
    manifiesto o si el PDF no está presente (no hay fallback silencioso)."""
    entries = parse_manifest(manifest)
    pid = _paper_id(paper_id)
    if pid not in entries:
        raise PaperNotFoundError(
            f"'{paper_id}' no está en el manifiesto ({manifest}). Ids: {sorted(entries)}")
    path = papers_dir / entries[pid]["filename"]
    if not path.exists():
        estado = entries[pid].get("estado", "?")
        raise PaperNotFoundError(
            f"'{pid}' está en el manifiesto (estado: {estado}) pero el PDF no está en "
            f"{path}. Obtenerlo con la receta de data/papers/README.md.")
    return path
