"""ingest.py — Bloque 1: ingesta y PERSISTENCIA de volcados de data.binance.vision.

Fuente: data.binance.vision — volcados históricos gratuitos, SIN cuenta ni API key.

PERSISTENCIA (prerrequisito, ya se perdieron datos una vez y el libro es caro de rebajar;
mismo criterio que `data/raw` de Dukascopy):
  - `data/raw_crypto/` es INMUTABLE: el pipeline sólo lee.
  - manifiesto `MANIFEST.sha256` con checksum SHA256 por archivo, versionado en git.
  - verificación contra el `.CHECKSUM` que publica Binance (SHA256) en la descarga.
  - `verify_manifest` FALLA si un checksum no cuadra.

HALLAZGO DE DISPONIBILIDAD (1.1, verificado 2026-08-24 por HTTP directo — el README de
binance/binance-public-data NO lista bookTicker, pero EXISTE):
  - bookTicker  (best bid/ask CON tamaños) → PRESENTE (~199 MB/día BTCUSDT). IMPRESCINDIBLE
    para OFI. Columnas: update_id, best_bid_price, best_bid_qty, best_ask_price,
    best_ask_qty, transaction_time, event_time.
  - aggTrades  → PRESENTE (~22 MB/día).
  - bookDepth  → PRESENTE (~0.5 MB/día; snapshots de profundidad).
"""

from __future__ import annotations

import hashlib
import urllib.request
import zipfile
from pathlib import Path

BASE_URL = "https://data.binance.vision/data"
RAW_ROOT = Path("data/raw_crypto")
MANIFEST = RAW_ROOT / "MANIFEST.sha256"
_CHUNK = 1 << 20


def daily_key(market: str, data_type: str, symbol: str, date: str) -> str:
    """Relative key (path + basename) for a daily dump. `market` e.g. 'futures/um'."""
    return f"{market}/daily/{data_type}/{symbol}/{symbol}-{data_type}-{date}"


def _url(rel_key: str) -> str:
    return f"{BASE_URL}/{rel_key}.zip"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(_CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def _parse_binance_checksum(text: str) -> str:
    # formato: "<sha256>  <filename>"
    return text.strip().split()[0].lower()


def download_daily(market: str, data_type: str, symbol: str, date: str, *,
                   root: Path = RAW_ROOT, timeout: float = 600.0) -> dict:
    """Download one daily dump + its .CHECKSUM into the immutable store, verifying the
    SHA256 Binance publishes. Returns a manifest record. Skips download if the file is
    already present AND matches its checksum (idempotent, never re-fetches 199 MB).
    """
    rel = daily_key(market, data_type, symbol, date)
    dest = root / f"{rel}.zip"
    dest.parent.mkdir(parents=True, exist_ok=True)
    chk_dest = Path(str(dest) + ".CHECKSUM")

    # checksum publicado por Binance
    if not chk_dest.exists():
        urllib.request.urlretrieve(_url(rel) + ".CHECKSUM", chk_dest)
    expected = _parse_binance_checksum(chk_dest.read_text())

    if dest.exists() and sha256_file(dest) == expected:
        actual = expected  # ya presente y válido
    else:
        urllib.request.urlretrieve(_url(rel), dest)
        actual = sha256_file(dest)
        if actual != expected:
            dest.unlink(missing_ok=True)
            raise ValueError(f"checksum mismatch para {rel}: esperado {expected}, got {actual}")

    return {"key": f"{rel}.zip", "sha256": actual, "bytes": dest.stat().st_size,
            "verified_against_binance": True}


def read_book_ticker(path: Path, *, nrows: int | None = None):
    """Read a bookTicker daily zip into a DataFrame, SORTED by (transaction_time,
    update_id). CRÍTICO: los volcados de futuros vienen DESORDENADOS en el tiempo (issue
    binance/binance-public-data#305); sin ordenar, el OFI —que depende de observaciones
    consecutivas— sería basura. El orden se restaura aquí, una vez, en el borde de lectura.
    """
    import pandas as pd

    cols = ["update_id", "best_bid_price", "best_bid_qty",
            "best_ask_price", "best_ask_qty", "transaction_time", "event_time"]
    with zipfile.ZipFile(path) as z:
        inner = z.namelist()[0]
        with z.open(inner) as fh:
            df = pd.read_csv(fh, names=cols, header=0, nrows=nrows,
                             dtype={"update_id": "int64", "transaction_time": "int64",
                                    "event_time": "int64", "best_bid_price": "float64",
                                    "best_bid_qty": "float64", "best_ask_price": "float64",
                                    "best_ask_qty": "float64"})
    return df.sort_values(["transaction_time", "update_id"]).reset_index(drop=True)


# ------------------------------------------------------------------ manifest
def _load_manifest(path: Path = MANIFEST) -> dict[str, str]:
    out: dict[str, str] = {}
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            sha, key = line.split(maxsplit=1)
            out[key] = sha
    return out


def update_manifest(records: list[dict], *, path: Path = MANIFEST) -> None:
    """Merge records into the versioned SHA256 manifest (sorted, deterministic)."""
    man = _load_manifest(path)
    for r in records:
        man[r["key"]] = r["sha256"]
    lines = ["# MANIFEST.sha256 — data/raw_crypto (versionado en git; los .zip NO).",
             "# <sha256>  <key relativo a data/raw_crypto/>"]
    lines += [f"{man[k]}  {k}" for k in sorted(man)]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def verify_manifest(*, root: Path = RAW_ROOT, path: Path = MANIFEST) -> list[str]:
    """Recompute SHA256 of every manifested file and return the list of MISMATCHES
    (empty = all good). A missing file counts as a mismatch. Este es el script de
    verificación que FALLA si un checksum no cuadra."""
    man = _load_manifest(path)
    bad = []
    for key, sha in man.items():
        fpath = root / key
        if not fpath.exists():
            bad.append(f"{key}: FALTA")
        elif sha256_file(fpath) != sha:
            bad.append(f"{key}: SHA256 no cuadra")
    return bad
