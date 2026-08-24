"""Tests de Bloque 1: ingesta, persistencia (manifiesto SHA256) y reporte de calidad."""

from __future__ import annotations

import zipfile

import pytest

from src.crypto import ingest, quality


def _make_book_ticker_zip(path, rows):
    """Write a bookTicker CSV (header + rows) into a .zip like Binance's dumps."""
    csv = "update_id,best_bid_price,best_bid_qty,best_ask_price,best_ask_qty,transaction_time,event_time\n"
    csv += "\n".join(",".join(str(c) for c in r) for r in rows) + "\n"
    inner = path.with_suffix("").name + ".csv"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr(inner, csv)


# rows: update_id, bidP, bidQ, askP, askQ, txtime, evtime  (txtime OUT OF ORDER on purpose)
_ROWS = [
    [10, 100.0, 5.0, 100.1, 4.0, 3000, 3000],   # later time first (disorder)
    [11, 100.0, 6.0, 100.1, 4.0, 3000, 3000],
    [1,  100.0, 5.0, 100.1, 4.0, 1000, 1000],
    [2,  100.1, 3.0, 100.2, 4.0, 1000, 1000],   # bid up
    [3,  100.1, 3.0, 100.2, 2.0, 2000, 2000],   # ask qty down
]


def test_read_book_ticker_sorts_by_time(tmp_path):
    z = tmp_path / "BTCUSDT-bookTicker-2024-01-02.zip"
    _make_book_ticker_zip(z, _ROWS)
    df = ingest.read_book_ticker(z)
    tt = df["transaction_time"].tolist()
    assert tt == sorted(tt)                       # restaurado el orden temporal
    # dentro del mismo timestamp, ordena por update_id
    assert df[df.transaction_time == 1000]["update_id"].tolist() == [1, 2]


def test_sha256_and_manifest_roundtrip(tmp_path):
    f = tmp_path / "a.zip"
    f.write_bytes(b"hello world")
    sha = ingest.sha256_file(f)
    man = tmp_path / "MANIFEST.sha256"
    ingest.update_manifest([{"key": "a.zip", "sha256": sha}], path=man)
    assert ingest.verify_manifest(root=tmp_path, path=man) == []      # coincide
    f.write_bytes(b"tampered")                                        # mutar el archivo
    bad = ingest.verify_manifest(root=tmp_path, path=man)
    assert bad and "no cuadra" in bad[0]                             # el verificador falla


def test_manifest_flags_missing_file(tmp_path):
    man = tmp_path / "MANIFEST.sha256"
    ingest.update_manifest([{"key": "ghost.zip", "sha256": "deadbeef"}], path=man)
    bad = ingest.verify_manifest(root=tmp_path, path=man)
    assert bad and "FALTA" in bad[0]


def test_quality_detects_disorder_but_not_kill(tmp_path):
    z = tmp_path / "BTCUSDT-bookTicker-2024-01-02.zip"
    _make_book_ticker_zip(z, _ROWS)
    rep = quality.quality_report(z)
    assert rep.out_of_order_frac > 0                 # detecta el interleaving
    assert not rep.kill                              # pero no es KILL (se ordena al leer)
    assert rep.zero_or_neg_price == 0 and rep.crossed_book == 0


def test_quality_flags_bad_prices_and_crossed_book(tmp_path):
    rows = [
        [1, 100.0, 5.0, 100.1, 4.0, 1000, 1000],
        [2, 0.0,   5.0, 100.1, 4.0, 2000, 2000],     # precio cero
        [3, 100.2, 5.0, 100.1, -1.0, 3000, 3000],    # bid>ask (cruzado) + size negativo
    ]
    z = tmp_path / "BTCUSDT-bookTicker-2024-01-02.zip"
    _make_book_ticker_zip(z, rows)
    rep = quality.quality_report(z)
    assert rep.zero_or_neg_price >= 1
    assert rep.crossed_book >= 1
    assert rep.neg_size >= 1


def test_daily_key_structure():
    k = ingest.daily_key("futures/um", "bookTicker", "BTCUSDT", "2024-01-02")
    assert k == "futures/um/daily/bookTicker/BTCUSDT/BTCUSDT-bookTicker-2024-01-02"
