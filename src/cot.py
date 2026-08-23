"""cot.py — CFTC Commitments of Traders: the first NON-PRICE signal source.

COT is positioning data (weekly): commercials hedge, non-commercials (large specs)
take the other side, and extreme imbalances mean-revert — a clean filter-4 mechanism.
Legacy Futures-Only report (specs vs commercials, longest history back to 1986;
Disaggregated changed methodology in 2009). Downloaded from the CFTC public API to
data/cot/<INSTRUMENT>.csv.

POINT-IN-TIME (donde vive el look-ahead): el reporte tiene FECHA DE DATOS (martes) y
se PUBLICA el viernes siguiente (~3 días de rezago). Una señal sólo puede usar el
dato desde su fecha de PUBLICACIÓN. Aquí el índice ES la fecha de publicación
(martes + 3 días = viernes), y `align_to_prices` hace asof: cada día de precio ve el
ÚLTIMO reporte ya PUBLICADO, nunca uno cuya fecha de datos aún no se ha publicado.
"""

from __future__ import annotations

import pandas as pd

from src import config

# Mapeo instrumento → contrato CFTC. `sign`: +1 si spec-largo-futuro = alcista en
# NUESTRO par; −1 si invertido (los futuros FX son divisa-extranjera/USD, así que
# largo yen/CAD futuro = corto USDJPY/USDCAD). Si falta un mapeo, falla visiblemente.
COT_CONTRACTS: dict[str, int] = {
    "EURUSD": +1, "GBPUSD": +1, "AUDUSD": +1,   # USD-quote: spec-long-foreign = long pair
    "USDJPY": -1, "USDCAD": -1,                  # USD-base: spec-long-foreign = SHORT pair
    "XAUUSD": +1, "XAGUSD": +1, "SPX500": +1,
}
PUBLICATION_LAG = pd.Timedelta(days=3)   # martes (fecha de datos) → viernes (publicación)


class CotNotMappedError(KeyError):
    """Un instrumento sin mapeo de contrato COT."""


def has_cot(instrument: str) -> bool:
    return instrument in COT_CONTRACTS and (config.ROOT / "data" / "cot" / f"{instrument}.csv").exists()


def load_cot(instrument: str) -> pd.DataFrame:
    """COT semanal indexado por FECHA DE PUBLICACIÓN (point-in-time).

    Columnas: net_spec (posicionamiento neto de especuladores, con signo del par,
    normalizado por open interest), y los conteos crudos. El índice es la fecha de
    publicación (fecha de datos + 3 días), NO la fecha de datos.
    """
    if instrument not in COT_CONTRACTS:
        raise CotNotMappedError(f"{instrument} sin mapeo en COT_CONTRACTS")
    path = config.ROOT / "data" / "cot" / f"{instrument}.csv"
    df = pd.read_csv(path, parse_dates=["date"])
    sign = COT_CONTRACTS[instrument]
    net = (df["nc_long"] - df["nc_short"]) * sign
    df["net_spec"] = net / df["oi"].where(df["oi"] > 0)   # normalizado por OI
    df["publish_date"] = df["date"] + PUBLICATION_LAG      # martes → viernes
    return df.set_index("publish_date").sort_index()[["date", "net_spec", "nc_long", "nc_short", "oi"]]


def align_to_prices(instrument: str, index: pd.DatetimeIndex) -> pd.Series:
    """`net_spec` alineado a un índice de precios diario, POINT-IN-TIME: cada día ve
    el último reporte ya PUBLICADO (asof sobre la fecha de publicación)."""
    cot = load_cot(instrument)["net_spec"]
    return cot.reindex(cot.index.union(index)).ffill().reindex(index)
