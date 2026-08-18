"""Tests de la capa de ingesta (sin red).

Prueban la LÓGICA (mapeo, decode lzma+struct, escritura atómica/idempotente),
NO que el layout binario coincida con Dukascopy — eso se verifica contra una
muestra real de EURUSD (ver test_decode_against_real_sample, skip por defecto).
"""

import lzma
import struct
from datetime import datetime, timezone
from pathlib import Path

import pytest

from src import config, dukascopy


# --- Mapeo de símbolos ------------------------------------------------------
def test_every_universe_instrument_is_mapped():
    dukascopy.validate_universe_mapping()  # no lanza
    for inst in config.INSTRUMENTS:
        assert dukascopy.dukascopy_symbol(inst)


def test_unmapped_symbol_is_a_visible_error():
    with pytest.raises(dukascopy.SymbolNotMappedError):
        dukascopy.dukascopy_symbol("NOPE")
    with pytest.raises(dukascopy.SymbolNotMappedError):
        dukascopy.validate_universe_mapping(("EURUSD", "NOPE"))


def test_universe_is_decorrelated():
    # Corrección del reviewer: energía (Brent) y Asia (Nikkei), no solo equity USA/EU.
    assert "JPN225" in config.INSTRUMENTS          # Asia
    assert "GER40" in config.INSTRUMENTS           # Europa
    assert "NAS100" not in config.INSTRUMENTS
    assert "UK100" not in config.INSTRUMENTS
    # BRENT retirado del universo activo (sparse) pero su mapeo se conserva.
    assert "BRENT" not in config.INSTRUMENTS
    assert "BRENT" in config.DUKASCOPY_SYMBOLS


# --- Decodificación (round-trip con el formato asumido) ---------------------
def _make_bi5(records: list[tuple]) -> bytes:
    """Construye un .bi5 sintético con el formato VERIFICADO (int prices, OCLHV).

    Cada record: (time_offset_s, open_i, close_i, low_i, high_i, volume).
    """
    raw = b"".join(dukascopy._RECORD.pack(*r) for r in records)
    return lzma.compress(raw)


def test_decode_bi5_roundtrip():
    # Dos velas diarias en enero (month0=0), precios int escalados ×1e5 (OCLHV).
    day = 86400
    records = [
        (0 * day, 110000, 112000, 109000, 113000, 1000.0),   # O C L H V
        (1 * day, 112000, 111000, 110000, 115000, 900.0),
    ]
    rows = dukascopy.decode_bi5(_make_bi5(records), year=2020, month0=0, point=1e5)
    assert len(rows) == 2
    # (date, open, high, low, close)
    d0 = rows[0]
    assert d0[0] == "2020-01-01"
    assert d0[1] == pytest.approx(1.10)   # open
    assert d0[2] == pytest.approx(1.13)   # high
    assert d0[3] == pytest.approx(1.09)   # low
    assert d0[4] == pytest.approx(1.12)   # close
    assert rows[1][0] == "2020-01-02"


def test_decode_empty_is_empty():
    assert dukascopy.decode_bi5(b"", year=2020, month0=0) == []


# --- Escritura atómica e idempotente ----------------------------------------
def test_write_atomic_and_idempotent(tmp_path):
    rows = [("2020-01-01", 1.1, 1.2, 1.0, 1.15), ("2020-01-02", 1.15, 1.3, 1.1, 1.25)]
    out = tmp_path / "EURUSD.csv"
    dukascopy._write_atomic(out, rows)
    first = out.read_bytes()
    assert not list(tmp_path.glob("*.tmp"))     # no deja temporales
    dukascopy._write_atomic(out, rows)          # idempotente
    assert out.read_bytes() == first
    assert first.decode().splitlines()[0] == "date,open,high,low,close"


def test_download_instrument_dedups_and_writes(tmp_path, monkeypatch):
    # Sin red: monkeypatch _fetch para devolver un .bi5 sintético por mes.
    day = 86400
    payload = _make_bi5([(0 * day, 110000, 112000, 109000, 113000, 10.0)])
    monkeypatch.setattr(dukascopy, "_fetch", lambda url: payload)
    start = datetime(2020, 1, 1, tzinfo=timezone.utc)
    end = datetime(2020, 1, 31, tzinfo=timezone.utc)
    out = dukascopy.download_instrument("EURUSD", start, end, raw_dir=tmp_path)
    assert out.exists()
    lines = out.read_text().splitlines()
    assert lines[0] == "date,open,high,low,close"
    assert len(lines) == 2  # header + una fila (deduplicada)


def test_network_failure_leaves_no_partial_raw(tmp_path, monkeypatch):
    # Un fallo de red tras los reintentos no debe dejar un crudo parcial.
    monkeypatch.setattr(dukascopy, "_BACKOFF_S", 0.0)  # tests rápidos

    def boom(url):
        raise ConnectionError("simulated network failure")

    monkeypatch.setattr(dukascopy, "_fetch", boom)
    start = datetime(2020, 1, 1, tzinfo=timezone.utc)
    end = datetime(2020, 1, 31, tzinfo=timezone.utc)
    with pytest.raises(ConnectionError):
        dukascopy.download_instrument("EURUSD", start, end, raw_dir=tmp_path)
    assert not list(tmp_path.glob("EURUSD.csv"))   # sin crudo
    assert not list(tmp_path.glob("*.tmp"))         # sin temporal parcial


# --- Verificación contra muestra real (la corres tú con un .bi5 de EURUSD) ---
@pytest.mark.skipif(
    not Path(__file__).parent.joinpath("fixtures/eurusd_sample.bi5").exists(),
    reason="Falta tests/fixtures/eurusd_sample.bi5 — coloca una muestra real para verificar el formato",
)
def test_decode_against_real_sample():
    sample = Path(__file__).parent / "fixtures/eurusd_sample.bi5"
    raw = sample.read_bytes()
    # El año/mes del sample deben coincidir con el archivo real que coloques.
    rows = dukascopy.decode_bi5(raw, year=2020, month0=0)
    assert rows, "El parser no produjo filas — ajustar constantes de formato (D2)"
    for date, o, h, low, c in rows:
        assert h >= max(o, c) >= min(o, c) >= low, f"OHLC incoherente en {date}"
