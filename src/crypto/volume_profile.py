"""volume_profile.py — H008: perfil de volumen (VAH/VAL/POC) desde aggTrades.

El PERFIL se define con el volumen traded por bucket de precio (aggTrades: price × quantity).
Resuelve (1.2) de la ficha: aggTrades BASTA — el perfil sale del volumen por nivel, y las
entradas límite en el borde del VA se llenan cuando un trade imprime en/pasa el nivel (el price
de aggTrades lo da). NO hace falta bookTicker.

  POC = bucket de mayor volumen.
  VA (área de valor) = expandir desde el POC hacia afuera, añadiendo en cada paso el vecino
      (arriba/abajo) de mayor volumen, hasta capturar `va_frac` (70%) del volumen total.
  VAH/VAL = borde superior/inferior del VA.
"""

from __future__ import annotations

import zipfile
from dataclasses import dataclass

AGG_COLS = ["agg_trade_id", "price", "quantity", "first_trade_id",
            "last_trade_id", "transact_time", "is_buyer_maker"]
BUCKET_USD = 10.0
VA_FRAC = 0.70


def read_agg_trades(path):
    """aggTrades daily zip → DataFrame (price, quantity, transact_time). Ligero."""
    import pandas as pd

    with zipfile.ZipFile(path) as z:
        with z.open(z.namelist()[0]) as fh:
            return pd.read_csv(fh, names=AGG_COLS, header=0,
                               usecols=["price", "quantity", "transact_time"],
                               dtype={"price": "float64", "quantity": "float64",
                                      "transact_time": "int64"})


@dataclass(frozen=True)
class Profile:
    poc: float          # centro del bucket de mayor volumen
    vah: float          # borde superior del área de valor
    val: float          # borde inferior del área de valor
    high: float         # máximo del día (nivel simple)
    low: float          # mínimo del día (nivel simple)
    total_volume: float
    va_volume_frac: float   # fracción de volumen efectivamente capturada por el VA


def build_profile(prices, quantities, *, bucket: float = BUCKET_USD,
                  va_frac: float = VA_FRAC) -> Profile:
    """Construye el perfil. `prices`/`quantities` son arrays alineados (un trade cada uno)."""
    import numpy as np

    prices = np.asarray(prices, float)
    quantities = np.asarray(quantities, float)
    high, low = float(prices.max()), float(prices.min())
    # bucket index por precio; volumen por bucket
    idx = np.floor(prices / bucket).astype("int64")
    lo_idx = idx.min()
    rel = idx - lo_idx
    vol = np.bincount(rel, weights=quantities)
    total = float(vol.sum())
    poc_rel = int(vol.argmax())
    # centro del bucket POC
    poc = (lo_idx + poc_rel) * bucket + bucket / 2.0

    # expandir el área de valor desde el POC hacia afuera por volumen
    target = va_frac * total
    lo, hi = poc_rel, poc_rel
    captured = vol[poc_rel]
    n = len(vol)
    while captured < target and (lo > 0 or hi < n - 1):
        up = vol[hi + 1] if hi < n - 1 else -1.0
        dn = vol[lo - 1] if lo > 0 else -1.0
        if up >= dn:
            hi += 1; captured += vol[hi]
        else:
            lo -= 1; captured += vol[lo]
    vah = (lo_idx + hi) * bucket + bucket        # borde superior del bucket más alto del VA
    val = (lo_idx + lo) * bucket                 # borde inferior del bucket más bajo del VA
    return Profile(poc=poc, vah=vah, val=val, high=high, low=low,
                   total_volume=total, va_volume_frac=captured / total if total else 0.0)


def profile_from_zip(path, **kw) -> Profile:
    df = read_agg_trades(path)
    return build_profile(df["price"].to_numpy(), df["quantity"].to_numpy(), **kw)
