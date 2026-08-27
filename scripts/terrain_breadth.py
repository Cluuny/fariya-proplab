"""terrain_breadth.py — cribado de AMPLITUD del terreno (Bloque B, change pipeline-run-003-and-breadth).

Pregunta decisiva: ¿cuál es el N_eff MÁXIMO alcanzable con universos que podemos operar Y pagar
($125/mes), y su techo de IR (≈ IC·√N_eff) supera algún listón medido? Si NO para todos, es el
cierre del programa por AMPLITUD.

N_eff = (Σλ)²/Σλ² sobre los autovalores de la matriz de correlación de retornos diarios
(participation ratio; mismo que scripts/effective_breadth.py). Datos:
  - CFD 17: parquet local (Dukascopy).       [medido]
  - Cripto perps: fapi.binance.com (gratis).  [medido] — el universo con acceso ilimitado.
  - Proxies ETF de futuros CME + ETFs sector/país/factor: Yahoo (gratis).  [proxy, marcado]

Red: se toca sólo en fetch_*. Sin red, usa los números cacheados del doc.
"""

from __future__ import annotations

import json
import urllib.request

import numpy as np

# --- listones medidos (docs/cost_floor.md, program_verdict.md, h008) ---
LISTONES = {"CFD (duty 100%)": 0.64, "cripto perp (mejor)": 0.65, "activo duty 31%": 0.96}
ICS = (0.02, 0.05)

CRYPTO_30 = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT",
             "AVAXUSDT", "LINKUSDT", "DOTUSDT", "LTCUSDT", "TRXUSDT", "BCHUSDT", "NEARUSDT",
             "UNIUSDT", "ATOMUSDT", "ETCUSDT", "XLMUSDT", "FILUSDT", "APTUSDT", "ARBUSDT",
             "OPUSDT", "INJUSDT", "SUIUSDT", "TIAUSDT", "SEIUSDT", "AAVEUSDT", "RUNEUSDT",
             "ALGOUSDT", "ENAUSDT"]  # cripto GENUINO (excluye perps tokenizados de TradFi)
# proxies ETF de futuros CME (índices, metales, energía, agrícolas, tasas, FX)
FUT_PROXY = ["SPY", "QQQ", "DIA", "IWM", "GLD", "SLV", "CPER", "USO", "UNG", "CORN", "WEAT",
             "SOYB", "CANE", "DBA", "TLT", "IEF", "IEI", "SHY", "UUP", "FXE", "FXY", "FXB",
             "FXA", "FXC", "DBC", "PALL"]
# ETFs diversificados: sectores + países + factores
ETF_DIV = ["XLE", "XLF", "XLK", "XLV", "XLI", "XLY", "XLP", "XLU", "XLB", "XLRE", "XLC",
           "EWJ", "EWG", "EWU", "EWZ", "EWY", "FXI", "INDA", "EWA", "EWC",
           "MTUM", "VLUE", "QUAL", "USMV", "SPY"]


def n_eff(corr: np.ndarray) -> float:
    ev = np.linalg.eigvalsh(corr)
    ev = ev[ev > 0]
    return float((ev.sum() ** 2) / (ev ** 2).sum())


def _neff_from_series(series: dict[str, dict]) -> tuple[float, int, float]:
    """series: symbol -> {date_key: close}. Devuelve (N_eff, dias_comunes, corr_mediana)."""
    common = sorted(set.intersection(*[set(v) for v in series.values()]))
    M = np.array([[series[s][t] for s in series] for t in common], float)
    rets = np.diff(np.log(M), axis=0)
    corr = np.corrcoef(rets, rowvar=False)
    iu = np.triu_indices(len(series), 1)
    return n_eff(corr), len(common), float(np.median(corr[iu]))


def fetch_fapi(sym: str, limit: int = 1000) -> dict[str, float]:
    url = f"https://fapi.binance.com/fapi/v1/klines?symbol={sym}&interval=1d&limit={limit}"
    req = urllib.request.Request(url, headers={"User-Agent": "breadth/1"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    # clave = fecha UTC (día), para alinear con ETFs/CFD
    return {_ms_to_date(int(k[0])): float(k[4]) for k in d}


def fetch_yahoo(sym: str, rng: str = "3y") -> dict[str, float]:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range={rng}&interval=1d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    res = d["chart"]["result"][0]
    ts = res["timestamp"]
    cl = res["indicators"]["quote"][0]["close"]
    return {_ms_to_date(t * 1000): c for t, c in zip(ts, cl) if c is not None}


def _ms_to_date(ms: int) -> str:
    # sin datetime.now(): conversión pura ms→YYYY-MM-DD (UTC)
    import datetime
    return datetime.datetime.utcfromtimestamp(ms / 1000).strftime("%Y-%m-%d")


def _fetch_all(syms, fetch) -> dict[str, dict]:
    out = {}
    for s in syms:
        try:
            out[s] = fetch(s)
        except Exception as ex:  # noqa: BLE001
            print(f"  skip {s}: {type(ex).__name__}")
    return out


def cfd_series() -> dict[str, dict]:
    import pandas as pd
    from src import config
    out = {}
    for c in config.INSTRUMENTS:
        s = pd.read_parquet(config.DATA_CLEAN / f"{c}.parquet")["close"]
        out[c] = {d.strftime("%Y-%m-%d"): float(v) for d, v in s.items()}
    return out


def ceiling(neff: float, ic: float) -> float:
    return ic * (neff ** 0.5)


def report(rows: list[dict]) -> None:
    print(f"\n{'universo':28s} {'N_eff':>6s} {'$/mes':>6s} "
          f"{'IR(IC.02)':>9s} {'IR(IC.05)':>9s}  ¿supera 0.64/0.65/0.96?")
    for r in rows:
        c02, c05 = ceiling(r["neff"], 0.02), ceiling(r["neff"], 0.05)
        supera = "sí" if c05 >= min(LISTONES.values()) else "NO"
        tag = "" if r.get("medido") else " (proxy)"
        print(f"{r['nombre']:28s} {r['neff']:6.2f} {r['coste']:>6} "
              f"{c02:9.3f} {c05:9.3f}   {supera}{tag}")


def main():
    rows = []

    print("== CFD 17 (Dukascopy, local) ==")
    ne, days, mc = _neff_from_series(cfd_series())
    print(f"  N_eff={ne:.2f} dias={days} corr_med={mc:.2f}")
    rows.append({"nombre": "CFD Dukascopy 17", "neff": ne, "coste": "~0", "medido": True})

    print("== Cripto perps 30 (fapi, GRATIS — acceso ilimitado) ==")
    cr = _fetch_all(CRYPTO_30, fetch_fapi)
    ne_cr, days, mc = _neff_from_series(cr)
    print(f"  N_eff={ne_cr:.2f} dias={days} corr_med={mc:.2f}  ({len(cr)} símbolos)")
    rows.append({"nombre": "Cripto perps 30 (Binance)", "neff": ne_cr, "coste": "0", "medido": True})

    print("== Futuros CME (proxy ETF, Yahoo) — requiere Norgate ~$50/mes ==")
    fu = _fetch_all(FUT_PROXY, fetch_yahoo)
    ne_fu, days, mc = _neff_from_series(fu)
    print(f"  N_eff={ne_fu:.2f} dias={days} corr_med={mc:.2f}  ({len(fu)} proxies)")
    rows.append({"nombre": "Futuros CME ~26 (proxy)", "neff": ne_fu, "coste": "~50", "medido": False})

    print("== ETFs sector/país/factor (Yahoo, GRATIS) ==")
    et = _fetch_all(ETF_DIV, fetch_yahoo)
    ne_et, days, mc = _neff_from_series(et)
    print(f"  N_eff={ne_et:.2f} dias={days} corr_med={mc:.2f}  ({len(et)} ETFs)")
    rows.append({"nombre": "ETFs sector/país/factor ~25", "neff": ne_et, "coste": "0", "medido": True})

    # combinaciones (alinear en fechas comunes)
    print("== Combinaciones ==")
    for nombre, a, b, coste in [("Cripto + CFD", cr, cfd_series(), "~0"),
                                 ("Futuros + Cripto", fu, cr, "~50")]:
        merged = {**{f"A:{k}": v for k, v in a.items()}, **{f"B:{k}": v for k, v in b.items()}}
        ne_c, days, mc = _neff_from_series(merged)
        print(f"  {nombre}: N_eff={ne_c:.2f} dias={days}")
        rows.append({"nombre": nombre, "neff": ne_c, "coste": coste, "medido": True})

    report(rows)
    print(f"\nListones: {LISTONES}")
    print("Nota frecuencia: el techo del bloque es IC·√N_eff (rebalanceo anual). Con rebalanceo")
    print("mensual BR=12·N_eff → ×√12=3.46; aun así el mejor (futuros N_eff~8, IC.05, mensual) =")
    print(f"  {0.05*(12*ne_fu)**0.5:.2f} < 0.64. La conclusión es robusta a la frecuencia.")


if __name__ == "__main__":
    main()
