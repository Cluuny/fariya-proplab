"""ofi.py — Bloque 2: Order Flow Imbalance (Cont, Kukanov & Stoikov 2011, arXiv 1011.6402).

Fórmula EXACTA de la sección 2.1, literal, con desigualdades NO estrictas. Para cada par
de observaciones consecutivas (n-1, n) del mejor bid/ask con tamaños:

  e_n = 1{P^B_n ≥ P^B_{n-1}}·q^B_n − 1{P^B_n ≤ P^B_{n-1}}·q^B_{n-1}
      − 1{P^A_n ≤ P^A_{n-1}}·q^A_n + 1{P^A_n ≥ P^A_{n-1}}·q^A_{n-1}

  OFI_k = Σ e_n sobre (t_{k-1}, t_k]

  ΔP_k = (P_k − P_{k-1})/δ   con P = mid = (P^B+P^A)/2 y δ = tick size.

Nota CRÍTICA: el input debe venir ORDENADO en el tiempo (ingest.read_book_ticker lo hace);
los volcados de futuros de Binance vienen interleaved (issue #305) y sin ordenar el OFI es
basura.
"""

from __future__ import annotations

# tick de precio de BTCUSDT perpetuo (USDⓈ-M). Verificable en el propio dato (44230.20 /
# 44230.30 → 0.10) y en las specs del contrato.
TICK_BTCUSDT = 0.10


def compute_events(df):
    """Vector de contribuciones e_n (longitud N-1) alineado a la observación n (1..N-1),
    junto con su timestamp `transaction_time`. `df` debe estar ordenado en el tiempo."""
    import numpy as np

    PB = df["best_bid_price"].to_numpy()
    qB = df["best_bid_qty"].to_numpy()
    PA = df["best_ask_price"].to_numpy()
    qA = df["best_ask_qty"].to_numpy()
    t = df["transaction_time"].to_numpy()

    PB0, PB1 = PB[:-1], PB[1:]
    qB0, qB1 = qB[:-1], qB[1:]
    PA0, PA1 = PA[:-1], PA[1:]
    qA0, qA1 = qA[:-1], qA[1:]

    # desigualdades NO estrictas (>=, <=), como en el paper
    e = (np.where(PB1 >= PB0, qB1, 0.0)
         - np.where(PB1 <= PB0, qB0, 0.0)
         - np.where(PA1 <= PA0, qA1, 0.0)
         + np.where(PA1 >= PA0, qA0, 0.0))
    return e, t[1:], (PB1 + PA1) / 2.0  # e_n, t_n, mid_n


def build_grid(df, *, dt_s: int = 10, tick: float = TICK_BTCUSDT,
               exclude_price_changing: bool = False):
    """Aggregate events onto a uniform time grid Δt (default 10 s). Returns a DataFrame
    indexed by bin start (ms) with columns: OFI, dP (mid change in TICKS), mid, depth,
    n_events. `depth` = media de (q^B+q^A)/2 en el bin (para la relación β∝1/profundidad).

    `exclude_price_changing=True` reproduce la verificación (c) del paper: excluye de OFI_k
    los eventos que cambian el mid (pero deja ΔP_k completo). R² baja pero se mantiene.
    """
    import numpy as np
    import pandas as pd

    e, t, mid = compute_events(df)
    dt_ms = dt_s * 1000
    bin_id = (t // dt_ms) * dt_ms

    if exclude_price_changing:
        mid_full = ((df["best_bid_price"].to_numpy() + df["best_ask_price"].to_numpy()) / 2.0)
        changed = mid_full[1:] != mid_full[:-1]     # el evento n movió el mid
        e = np.where(changed, 0.0, e)

    depth_all = (df["best_bid_qty"].to_numpy() + df["best_ask_qty"].to_numpy()) / 2.0
    depth_n = depth_all[1:]  # alineado a n

    g = pd.DataFrame({"bin": bin_id, "e": e, "mid": mid, "depth": depth_n})
    agg = g.groupby("bin").agg(OFI=("e", "sum"), mid=("mid", "last"),
                               depth=("depth", "mean"), n_events=("e", "size"))
    agg = agg.sort_index()
    agg["dP"] = agg["mid"].diff() / tick
    return agg.dropna(subset=["dP"])


def trade_imbalance(agg_trades, *, dt_s: int = 10):
    """Trade imbalance TI_k por bin de Δt, a partir de aggTrades. Signo del agresor:
    is_buyer_maker=True → agresor VENDEDOR → −qty; False → agresor COMPRADOR → +qty.
    Devuelve una Series indexada por bin start (ms)."""
    import numpy as np
    import pandas as pd

    t = agg_trades["transact_time"].to_numpy()
    qty = agg_trades["quantity"].to_numpy()
    buyer_maker = agg_trades["is_buyer_maker"].to_numpy().astype(bool)
    signed = np.where(buyer_maker, -qty, qty)
    dt_ms = dt_s * 1000
    bin_id = (t // dt_ms) * dt_ms
    return pd.Series(signed, index=bin_id).groupby(level=0).sum().rename("TI")
