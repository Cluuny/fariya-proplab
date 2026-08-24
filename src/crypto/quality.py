"""quality.py — Bloque 1.5: reporte de calidad del libro (mismo criterio que mató a BRENT).

Comprueba, sobre un volcado bookTicker: huecos temporales, timestamps duplicados o
DESORDENADOS (los volcados de futuros vienen interleaved, issue #305), precios cero o
negativos, tamaños negativos, libro cruzado (bid≥ask) y períodos de mantenimiento del
exchange (huecos largos). KILL si falta >25% de un período (hora).
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Un hueco entre updates mayor que esto se cuenta como "falta de datos" (bookTicker de BTC
# actualiza muchas veces por segundo; 5 s sin un solo update es anómalo / mantenimiento).
GAP_THRESHOLD_MS = 5_000
KILL_MISSING_FRACTION = 0.25   # KILL si alguna hora pierde > 25% de su tiempo


@dataclass
class QualityReport:
    symbol: str
    n_rows: int
    out_of_order_frac: float          # fracción de filas con t < t previo en el orden RAW
    dup_key_count: int                # (transaction_time, update_id) duplicados
    zero_or_neg_price: int
    neg_size: int
    crossed_book: int                 # bid >= ask
    max_gap_s: float
    worst_hour_missing_frac: float
    hours_over_budget: list[int] = field(default_factory=list)
    kill: bool = False
    notes: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        v = "KILL" if self.kill else "OK"
        L = [f"# Reporte de calidad — {self.symbol}  [{v}]", "",
             f"- filas: {self.n_rows:,}",
             f"- fuera de orden (raw): {self.out_of_order_frac:.1%} "
             f"(se corrige ordenando por (transaction_time, update_id) al leer)",
             f"- claves (ts,update_id) duplicadas: {self.dup_key_count:,}",
             f"- precios cero/negativos: {self.zero_or_neg_price:,}",
             f"- tamaños negativos: {self.neg_size:,}",
             f"- libro cruzado (bid≥ask): {self.crossed_book:,}",
             f"- hueco máximo: {self.max_gap_s:.1f} s",
             f"- peor hora, fracción faltante: {self.worst_hour_missing_frac:.1%} "
             f"(KILL si > {KILL_MISSING_FRACTION:.0%})"]
        if self.hours_over_budget:
            L.append(f"- horas sobre presupuesto de hueco: {self.hours_over_budget}")
        for n in self.notes:
            L.append(f"- NOTA: {n}")
        return "\n".join(L) + "\n"


def quality_report(path, *, symbol: str = "BTCUSDT") -> QualityReport:
    """Full quality pass over a bookTicker daily zip. Reads RAW order first (to measure
    disorder), then sorts for gap analysis."""
    import numpy as np

    from src.crypto import ingest

    raw = ingest.read_book_ticker(path)  # ya ordenado; para el desorden leemos aparte
    # medir desorden sobre el orden ORIGINAL del archivo:
    raw_unsorted = _read_raw_unsorted(path)
    tt = raw_unsorted["transaction_time"].to_numpy()
    out_of_order_frac = float((np.diff(tt) < 0).mean()) if len(tt) > 1 else 0.0

    df = raw  # ordenado
    dup_key = int(df.duplicated(["transaction_time", "update_id"]).sum())
    zero_neg_price = int(((df["best_bid_price"] <= 0) | (df["best_ask_price"] <= 0)).sum())
    neg_size = int(((df["best_bid_qty"] < 0) | (df["best_ask_qty"] < 0)).sum())
    crossed = int((df["best_bid_price"] >= df["best_ask_price"]).sum())

    # huecos temporales por hora
    t = df["transaction_time"].to_numpy()
    gaps = np.diff(t)
    max_gap_s = float(gaps.max() / 1000.0) if len(gaps) else 0.0
    # atribuir el tiempo de cada hueco > umbral a la hora en que empieza
    hour = ((t - t[0]) // 3_600_000).astype("int64")  # índice de hora desde el inicio
    big = gaps > GAP_THRESHOLD_MS
    missing_ms_by_hour: dict[int, float] = {}
    for h, g, is_big in zip(hour[:-1], gaps, big):
        if is_big:
            missing_ms_by_hour[int(h)] = missing_ms_by_hour.get(int(h), 0.0) + float(g)
    worst = max((v / 3_600_000 for v in missing_ms_by_hour.values()), default=0.0)
    over = sorted(h for h, v in missing_ms_by_hour.items() if v / 3_600_000 > KILL_MISSING_FRACTION)

    rep = QualityReport(
        symbol=symbol, n_rows=len(df), out_of_order_frac=out_of_order_frac,
        dup_key_count=dup_key, zero_or_neg_price=zero_neg_price, neg_size=neg_size,
        crossed_book=crossed, max_gap_s=max_gap_s, worst_hour_missing_frac=worst,
        hours_over_budget=over)
    rep.kill = worst > KILL_MISSING_FRACTION
    if out_of_order_frac > 0.01:
        rep.notes.append("volcado interleaved (issue #305): se ORDENA al leer, no es KILL")
    if max_gap_s > GAP_THRESHOLD_MS / 1000:
        rep.notes.append(f"hueco de {max_gap_s:.0f}s: posible mantenimiento del exchange")
    return rep


def _read_raw_unsorted(path):
    """Read bookTicker WITHOUT sorting, to measure the raw out-of-order fraction."""
    import zipfile

    import pandas as pd

    cols = ["update_id", "best_bid_price", "best_bid_qty",
            "best_ask_price", "best_ask_qty", "transaction_time", "event_time"]
    with zipfile.ZipFile(path) as z:
        with z.open(z.namelist()[0]) as fh:
            return pd.read_csv(fh, names=cols, header=0,
                               usecols=["transaction_time"], dtype={"transaction_time": "int64"})
