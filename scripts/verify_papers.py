"""verify_papers.py — verificación del corpus de papers (mismo patrón que raw/raw_crypto).

  - lista qué entradas del MANIFEST tienen archivo presente y cuáles no
  - calcula SHA256 de los presentes y lo compara con el manifiesto
  - si un paper está presente pero SIN SHA256 registrado, lo calcula y avisa para añadirlo
  - FALLA (exit 1) si un SHA256 no cuadra (archivo corrupto o sustituido)
  - FALLA (exit 2) si detecta un PDF trackeado en git (copyright en repo público)

El manifiesto se versiona; los binarios NO.
"""

from __future__ import annotations

import subprocess
import sys

from src.pipeline import papers


def _tracked_pdfs() -> list[str]:
    try:
        out = subprocess.run(["git", "ls-files", "data/papers"], capture_output=True,
                             text=True, check=True).stdout
    except Exception as ex:  # noqa: BLE001
        print(f"[warn] no pude consultar git ls-files: {ex}")
        return []
    return [ln for ln in out.splitlines() if ln.lower().endswith(".pdf")]


def main() -> int:
    entries = papers.parse_manifest()
    print(f"MANIFEST: {len(entries)} entradas\n")

    mismatch = False
    missing_sha_warn = False
    for pid, e in sorted(entries.items()):
        path = papers.PAPERS_DIR / e["filename"]
        estado = e.get("estado", "?")
        if not path.exists():
            if estado == "no_obtenible":
                # estado VÁLIDO: la cita se conserva, el archivo no es obtenible (no es un pendiente real)
                print(f"  [no_obtenible] {pid}  (cita conservada; sin archivo, no falla)")
            else:
                print(f"  [ausente]  {pid}  (estado: {estado})")
            continue
        actual = papers.sha256_file(path)
        recorded = e.get("sha256")
        if recorded is None:
            print(f"  [SIN SHA]  {pid}  → calcular y añadir al MANIFEST:\n"
                  f"             SHA256: {actual}")
            missing_sha_warn = True
        elif actual == recorded:
            print(f"  [OK]       {pid}")
        else:
            print(f"  [MISMATCH] {pid}: manifiesto {recorded[:12]}… vs archivo {actual[:12]}…")
            mismatch = True

    tracked = _tracked_pdfs()
    if tracked:
        print("\n[ERROR] PDFs TRACKEADOS en git (copyright en repo público):")
        for t in tracked:
            print(f"  - {t}   → sacar con: git rm --cached '{t}'")
        return 2

    if mismatch:
        print("\n[FALLO] al menos un SHA256 no cuadra (archivo corrupto o sustituido).")
        return 1
    if missing_sha_warn:
        print("\n[aviso] hay papers presentes sin SHA256 en el manifiesto (ver arriba).")
    print("\nOK: manifiesto consistente, ningún PDF trackeado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
