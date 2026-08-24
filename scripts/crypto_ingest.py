"""crypto_ingest.py — runner de Bloque 1: descarga, verifica, manifiesta y reporta calidad.

Uso:
    python -m scripts.crypto_ingest download --symbol BTCUSDT --type bookTicker \
        --start 2024-01-02 --days 5
    python -m scripts.crypto_ingest verify        # re-verifica el manifiesto (falla si no cuadra)
    python -m scripts.crypto_ingest quality --symbol BTCUSDT --date 2024-01-02

Recomendación (1.3): empezar con 5 días, MEDIR GB/tiempo antes de escalar. No bajar meses
de golpe (un día de bookTicker BTCUSDT ≈ 199 MB comprimido, ~18.5M filas).
"""

from __future__ import annotations

import argparse
from datetime import date, timedelta

from src.crypto import ingest, quality


def _dates(start: str, days: int) -> list[str]:
    y, m, d = (int(x) for x in start.split("-"))
    d0 = date(y, m, d)
    return [(d0 + timedelta(days=i)).isoformat() for i in range(days)]


def cmd_download(args):
    import time

    recs, total_bytes = [], 0
    for dd in _dates(args.start, args.days):
        t0 = time.time()
        rec = ingest.download_daily("futures/um", args.type, args.symbol, dd)
        total_bytes += rec["bytes"]
        print(f"  {args.symbol} {args.type} {dd}: {rec['bytes']/1e6:.1f} MB "
              f"sha OK, {time.time()-t0:.1f}s")
        recs.append(rec)
    ingest.update_manifest(recs)
    print(f"total {total_bytes/1e9:.2f} GB · manifiesto actualizado ({len(recs)} archivos)")


def cmd_verify(args):
    bad = ingest.verify_manifest()
    if bad:
        print("VERIFICACIÓN FALLÓ:")
        for b in bad:
            print("  -", b)
        raise SystemExit(1)
    print("manifiesto OK: todos los checksums cuadran.")


def cmd_quality(args):
    key = ingest.daily_key("futures/um", "bookTicker", args.symbol, args.date)
    rep = quality.quality_report(ingest.RAW_ROOT / f"{key}.zip", symbol=args.symbol)
    print(rep.to_markdown())
    if rep.kill:
        raise SystemExit(2)


def main(argv=None):
    p = argparse.ArgumentParser(description="Ingesta de datos cripto (Bloque 1)")
    sub = p.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("download")
    d.add_argument("--symbol", default="BTCUSDT")
    d.add_argument("--type", default="bookTicker", choices=["bookTicker", "aggTrades", "bookDepth"])
    d.add_argument("--start", required=True)
    d.add_argument("--days", type=int, default=5)
    d.set_defaults(fn=cmd_download)
    sub.add_parser("verify").set_defaults(fn=cmd_verify)
    q = sub.add_parser("quality")
    q.add_argument("--symbol", default="BTCUSDT")
    q.add_argument("--date", required=True)
    q.set_defaults(fn=cmd_quality)
    args = p.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
