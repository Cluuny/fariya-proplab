"""dukascopy.py — Ingesta automática de barras diarias EOD desde Dukascopy.

Descarga los archivos `.bi5` de velas diarias del feed público de Dukascopy para
el universo configurado, los decodifica a (fecha, OHLC) y los escribe en
`data/raw/` en el formato que `loaders` consume. Python puro (stdlib: urllib,
lzma, struct) — sin dependencias de runtime ni de Node.

`data/raw/` se mantiene inmutable para `loaders`: la escritura es atómica
(temporal → rename) e idempotente.

⚠️  FORMATO SIN VERIFICAR CONTRA EL FEED REAL. El layout binario del `.bi5` de
    velas y el esquema de URL están tomados del formato conocido por la comunidad
    (Dukascopy no lo publica oficialmente). Las constantes marcadas abajo se
    verifican/ajustan contra UNA muestra real de EURUSD antes de considerarse
    correctas (ver el test de verificación y la tarea D2 del change). Los tests
    con fixtures prueban la LÓGICA de decodificación (lzma + struct + fecha), no
    que el layout coincida con Dukascopy.
"""

from __future__ import annotations

import lzma
import struct
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src import config

# --------------------------------------------------------------------------- #
# Constantes de formato — VERIFICAR CONTRA MUESTRA REAL (D2)                   #
# --------------------------------------------------------------------------- #
_BASE_URL = "https://datafeed.dukascopy.com/datafeed"

# Esquema de URL de velas diarias (mes 0-indexado, quirk conocido de Dukascopy):
#   {BASE}/{SYMBOL}/{YYYY}/{MM0:02d}/BID_candles_day_1.bi5
# ASUNCIÓN: un archivo por (instrumento, mes) con las velas diarias del mes.
_URL_TEMPLATE = "{base}/{symbol}/{year}/{month0:02d}/BID_candles_day_1.bi5"

# Layout del registro de vela — VERIFICADO contra una muestra real de EURUSD:
# big-endian, int32 (offset de tiempo) + 4 int32 (precios ESCALADOS) + float32
# (volumen). Orden de campos OCLHV (quirk de Dukascopy: open, close, low, high).
_RECORD = struct.Struct(">i i i i i f")   # 24 bytes
_FIELD_ORDER = ("open", "close", "low", "high", "volume")

# El offset de tiempo del registro está en SEGUNDOS desde el inicio del mes.
_TIME_UNIT_SECONDS = 1.0

# Factor de escala de precios por defecto (5-digit FX: 112120 → 1.12120). Es
# COSMÉTICO para este pipeline: los retornos (pct_change) y el Sharpe son
# invariantes a la escala, así que un factor equivocado no corrompe ninguna
# métrica; sólo cambia el nivel absoluto mostrado. Se ajusta por instrumento
# vía `config.DUKASCOPY_POINT`.
_DEFAULT_POINT = 1e5

# Timeout y reintentos de red.
_TIMEOUT_S = 30
_MAX_RETRIES = 4
_BACKOFF_S = 2.0


class SymbolNotMappedError(KeyError):
    """Un instrumento del universo no tiene símbolo de Dukascopy."""


# --------------------------------------------------------------------------- #
# Mapeo de símbolos                                                           #
# --------------------------------------------------------------------------- #
def dukascopy_symbol(instrument: str) -> str:
    """Devuelve el símbolo de Dukascopy o falla de forma visible si no hay mapeo."""
    try:
        return config.DUKASCOPY_SYMBOLS[instrument]
    except KeyError as exc:
        raise SymbolNotMappedError(
            f"Instrumento '{instrument}' sin mapeo en DUKASCOPY_SYMBOLS"
        ) from exc


def validate_universe_mapping(
    universe: tuple[str, ...] = config.INSTRUMENTS,
) -> None:
    """Falla si algún instrumento del universo no tiene mapeo."""
    missing = [i for i in universe if i not in config.DUKASCOPY_SYMBOLS]
    if missing:
        raise SymbolNotMappedError(f"Sin mapeo de Dukascopy: {missing}")


# --------------------------------------------------------------------------- #
# URL y decodificación                                                        #
# --------------------------------------------------------------------------- #
def _build_url(symbol: str, year: int, month0: int) -> str:
    return _URL_TEMPLATE.format(
        base=_BASE_URL, symbol=symbol, year=year, month0=month0
    )


def decode_bi5(
    raw: bytes, year: int, month0: int, point: float = _DEFAULT_POINT
) -> list[tuple]:
    """Decodifica un `.bi5` de velas diarias a filas (date, open, high, low, close).

    `raw` es el contenido comprimido con LZMA-alone. Cada registro de tamaño fijo
    (`_RECORD`) lleva un offset de tiempo (segundos desde el inicio del mes) y los
    precios OCLHV como enteros escalados por `point`. El volumen se descarta (no lo
    usa `loaders`). `point` es cosmético (los retornos son invariantes a la escala).
    """
    if not raw:
        return []
    data = lzma.decompress(raw)  # FORMAT_AUTO maneja LZMA-alone
    month_start = datetime(year, month0 + 1, 1, tzinfo=timezone.utc)
    rows: list[tuple] = []
    for off in range(0, len(data) - len(data) % _RECORD.size, _RECORD.size):
        t, *vals = _RECORD.unpack_from(data, off)
        fields = dict(zip(_FIELD_ORDER, vals))
        ts = month_start + timedelta(seconds=t * _TIME_UNIT_SECONDS)
        rows.append(
            (
                ts.date().isoformat(),
                fields["open"] / point,
                fields["high"] / point,
                fields["low"] / point,
                fields["close"] / point,
            )
        )
    return rows


# --------------------------------------------------------------------------- #
# Descarga                                                                     #
# --------------------------------------------------------------------------- #
def _fetch(url: str) -> bytes:
    """Descarga con reintentos acotados y backoff. 404 → b'' (mes sin datos)."""
    from time import sleep

    last_exc: Exception | None = None
    for attempt in range(_MAX_RETRIES):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "prop-lab/0.1"})
            with urllib.request.urlopen(req, timeout=_TIMEOUT_S) as resp:
                return resp.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return b""  # mes sin datos (feriado/instrumento nuevo)
            last_exc = exc
        except (urllib.error.URLError, TimeoutError) as exc:
            last_exc = exc
        if attempt < _MAX_RETRIES - 1:
            sleep(_BACKOFF_S * (attempt + 1))
    raise ConnectionError(f"No se pudo descargar {url}: {last_exc}")


def _write_atomic(path: Path, rows: list[tuple]) -> None:
    """Escribe CSV de forma atómica (tmp → rename) para no dejar crudos parciales."""
    import csv

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "open", "high", "low", "close"])
        w.writerows(rows)
    tmp.replace(path)  # atómico en el mismo filesystem


def _months(start: datetime, end: datetime):
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        yield y, m - 1  # month0 (0-indexado)
        m += 1
        if m > 12:
            m = 1
            y += 1


def download_instrument(
    instrument: str, start: datetime, end: datetime, raw_dir: Path = config.DATA_RAW
) -> Path:
    """Descarga todas las velas diarias de un instrumento y las escribe a data/raw/."""
    symbol = dukascopy_symbol(instrument)
    point = config.DUKASCOPY_POINT.get(instrument, _DEFAULT_POINT)
    rows: list[tuple] = []
    for year, month0 in _months(start, end):
        raw = _fetch(_build_url(symbol, year, month0))
        rows.extend(decode_bi5(raw, year, month0, point))
    rows.sort(key=lambda r: r[0])
    # Deduplicar por fecha (conservar el último), robustez ante solapes.
    dedup: dict[str, tuple] = {r[0]: r for r in rows}
    out = raw_dir / f"{instrument}.csv"
    _write_atomic(out, list(dedup.values()))
    return out


def download(
    universe: tuple[str, ...] = config.INSTRUMENTS,
    *,
    start: datetime,
    end: datetime,
    raw_dir: Path = config.DATA_RAW,
) -> list[Path]:
    validate_universe_mapping(universe)
    return [download_instrument(i, start, end, raw_dir) for i in universe]


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Descarga barras diarias EOD de Dukascopy.")
    ap.add_argument("--from", dest="start", default="2005-01-01")
    ap.add_argument("--to", dest="end", default=None)
    args = ap.parse_args()
    start = datetime.fromisoformat(args.start).replace(tzinfo=timezone.utc)
    end = (
        datetime.fromisoformat(args.end).replace(tzinfo=timezone.utc)
        if args.end
        else datetime.now(timezone.utc)
    )
    validate_universe_mapping()
    print(f"Descargando {len(config.INSTRUMENTS)} instrumentos {start.date()}→{end.date()} …")
    for path in download(start=start, end=end):
        print(f"  {path}")
    print("Listo. Ahora: python -m src.loaders")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
