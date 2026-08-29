"""crypto_vol_screen.py — cribado de amplitud + prima de volatilidad en cripto (Deribit).

NO es una hipótesis: es un CRIBADO (como COT/H002/OFI). No consume intentos, no toca holdout. Mide
dos cosas con datos REALES de la API pública gratuita de Deribit (+ Binance para el spot):
  Bloque 2 — ¿cuánta AMPLITUD aporta la superficie de vol? (N_eff, participation ratio)
  Bloque 3 — ¿cuál es el IC de la PRIMA DE VOLATILIDAD? (IV−RV), con colas.

COBERTURA REAL (Bloque 1.1, verificado): DVOL (índice de vol implícita ~30d ATM) BTC/ETH diario
back to ~2021 (cap 1000 pts/llamada → ventana ~2022-12→2025-08); OHLC del perp para la vol
realizada; **la CADENA HISTÓRICA de opciones NO es reconstruible gratis** (get_instruments
expired=true sólo retiene ~semanas) → NO se pueden construir 7d/90d ATM, skew 25-delta ni pendiente
de estructura temporal. Se mide lo construible (DVOL, RV, prima IV−RV); el resto se reporta como
limitación. La amplitud medida es una COTA INFERIOR (las series de skew/estructura que faltan
añadirían dimensiones ortogonales que no podemos medir).
"""

from __future__ import annotations

import json
import urllib.request

import numpy as np

DERIBIT = "https://www.deribit.com/api/v2/public"
CRYPTO_30 = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT",
             "AVAXUSDT", "LINKUSDT", "DOTUSDT", "LTCUSDT", "TRXUSDT", "BCHUSDT", "NEARUSDT",
             "UNIUSDT", "ATOMUSDT", "ETCUSDT", "XLMUSDT", "FILUSDT", "APTUSDT", "ARBUSDT",
             "OPUSDT", "INJUSDT", "SUIUSDT", "TIAUSDT", "SEIUSDT", "AAVEUSDT", "RUNEUSDT",
             "ALGOUSDT", "ENAUSDT"]
LISTON = 0.65   # cripto perp mejor caso; el compromiso de Bloque 4


def _get(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "vol/1"}), timeout=40))


def _ms_to_date(ms):
    import datetime
    return datetime.datetime.fromtimestamp(ms / 1000, datetime.timezone.utc).strftime("%Y-%m-%d")


def dvol(cur, end=1756425600000):
    d = _get(f"{DERIBIT}/get_volatility_index_data?currency={cur}&start_timestamp=1609459200000"
             f"&end_timestamp={end}&resolution=1D")["result"]["data"]
    return {_ms_to_date(r[0]): float(r[4]) for r in d}   # close del índice de vol implícita (%)


def perp_close(cur, end=1756425600000):
    r = _get(f"{DERIBIT}/get_tradingview_chart_data?instrument_name={cur}-PERPETUAL&resolution=1D"
             f"&start_timestamp=1609459200000&end_timestamp={end}")["result"]
    return {_ms_to_date(t): float(c) for t, c in zip(r["ticks"], r["close"])}


def fapi_daily(sym, limit=1000):
    d = _get(f"https://fapi.binance.com/fapi/v1/klines?symbol={sym}&interval=1d&limit={limit}")
    return {_ms_to_date(int(k[0])): float(k[4]) for k in d}


def n_eff(corr):
    ev = np.linalg.eigvalsh(corr); ev = ev[ev > 0]
    return float((ev.sum() ** 2) / (ev ** 2).sum())


def _series_neff(series: dict[str, dict]) -> float:
    common = sorted(set.intersection(*[set(v) for v in series.values()]))
    M = np.array([[series[s][t] for s in series] for t in common], float)
    rets = np.diff(M, axis=0)  # cambios diarios (para vol) o log-ret (spot, ya en log abajo)
    return n_eff(np.corrcoef(rets, rowvar=False))


def main():
    print("=== Bloque 1 — ingesta (Deribit + Binance) ===")
    iv = {c: dvol(c) for c in ("BTC", "ETH")}
    px = {c: perp_close(c) for c in ("BTC", "ETH")}
    print(f"  DVOL BTC {len(iv['BTC'])}d, ETH {len(iv['ETH'])}d; perp OHLC BTC {len(px['BTC'])}d")

    # construir series por moneda: iv_30 (=DVOL), rv_30, prima = iv-rv
    import pandas as pd
    vol_series = {}       # series de VOL (para amplitud): cambios diarios
    prem = {}             # prima IV-RV por moneda (nivel, para el IC)
    ivp = {}              # iv nivel
    for c in ("BTC", "ETH"):
        s_iv = pd.Series(iv[c]).sort_index()
        s_px = pd.Series(px[c]).sort_index()
        common = s_iv.index.intersection(s_px.index)
        s_iv, s_px = s_iv[common], s_px[common]
        logret = np.log(s_px).diff()
        rv30 = logret.rolling(30).std() * np.sqrt(365) * 100   # vol realizada anualizada %
        p = s_iv - rv30
        vol_series[f"IV_{c}"] = s_iv.to_dict()
        vol_series[f"RV_{c}"] = rv30.dropna().to_dict()
        vol_series[f"PREM_{c}"] = p.dropna().to_dict()
        prem[c] = p
        ivp[c] = s_iv

    # spot-30 (log-precio, para que _series_neff use log-ret)
    spot = {}
    for s in CRYPTO_30:
        try:
            spot[s] = {d: np.log(v) for d, v in fapi_daily(s).items()}
        except Exception:
            pass
    print(f"  spot-30 símbolos: {len(spot)}")

    # ============ Bloque 2 — amplitud ============
    print("\n=== Bloque 2 — AMPLITUD (N_eff, participation ratio) ===")
    ne_spot = _series_neff(spot)
    volS = {k: {d: np.log(max(v, 1e-6)) for d, v in s.items()} for k, s in vol_series.items()}  # log de niveles de vol
    ne_vol = _series_neff(volS)
    ne_comb = _series_neff({**spot, **volS})
    print(f"  a) spot cripto solo:        N_eff = {ne_spot:.2f}  (referencia terrain_breadth 2.16)")
    print(f"  c) series de vol solas:     N_eff = {ne_vol:.2f}  ({len(volS)} series)")
    print(f"  b) spot + vol combinado:    N_eff = {ne_comb:.2f}")
    print(f"  APORTE MARGINAL por serie de vol (N_eff(spot+serie) − N_eff(spot)):")
    for k, s in volS.items():
        d = _series_neff({**spot, k: s}) - ne_spot
        deriv = "  ← derivable del spot (debe aportar poco)" if k.startswith("RV") else ""
        print(f"     +{k:10s} Δ {d:+.2f}{deriv}")

    # ============ Bloque 3 — IC de la prima de volatilidad ============
    print("\n=== Bloque 3 — IC de la PRIMA DE VOLATILIDAD ===")
    print("  señal = zscore(IV_30d − RV_30d backward, conocida en t). DOS aproximaciones del objetivo:")
    print("   (A) carry realizado = IV_t − RV_realizada[t,t+30] — la 'plata' del short-vol, PERO comparte")
    print("       IV_t con la señal → correlación MECÁNICA que INFLA el IC (nivel de IV, no timing).")
    print("   (B) cambio de IV = −(IV_{t+30}−IV_t) — proxy sancionado por el bloque; NO comparte nivel →")
    print("       TIMING puro (¿una prima alta predice que la IV cae?).")
    H = 30
    rng = np.random.default_rng(20260829)
    results = {}
    for name, use_payoff in (("A carry (IV−RV_fwd)", True), ("B timing (−ΔIV)", False)):
        sig_all, tgt_all = [], []
        for c in ("BTC", "ETH"):
            s_iv = ivp[c]; p = prem[c].dropna(); idx = p.index
            s_px = pd.Series(px[c]).sort_index(); logret = np.log(s_px).diff()
            for t in idx[:-H]:
                loc = idx.get_loc(t)
                if loc + H >= len(idx):
                    continue
                fwd = idx[loc + H]
                if use_payoff:
                    w = logret.loc[t:fwd]
                    if len(w) < 10:
                        continue
                    tgt_v = float(s_iv.loc[t] - w.std() * np.sqrt(365) * 100)
                else:
                    tgt_v = float(-(s_iv.loc[fwd] - s_iv.loc[t]))
                sig_all.append(float(p.loc[t])); tgt_all.append(tgt_v)
        sig_z = (np.array(sig_all) - np.mean(sig_all)) / np.std(sig_all)
        tgt = np.array(tgt_all); n = len(sig_z)
        ic = float(np.corrcoef(sig_z, tgt)[0, 1])
        ic_indep = float(np.corrcoef(sig_z[::H], tgt[::H])[0, 1])
        n_indep = len(sig_z[::H])
        boots = []
        for _ in range(2000):
            starts = rng.integers(0, n - H, size=max(1, n // H))
            idxb = np.concatenate([np.arange(s, s + H) for s in starts]); idxb = idxb[idxb < n]
            boots.append(np.corrcoef(sig_z[idxb], tgt[idxb])[0, 1])
        lo, hi = np.percentile(boots, [2.5, 97.5])
        sk_r, ku_r = float(pd.Series(tgt).skew()), float(pd.Series(tgt).kurt())
        results[name] = dict(ic=ic, ic_indep=ic_indep, n=n, n_indep=n_indep, lo=lo, hi=hi, sk=sk_r, ku=ku_r)
        print(f"\n  [{name}] IC solapado {ic:+.3f} (n={n}), IC95 bloque [{lo:+.3f},{hi:+.3f}]; "
              f"IC no-solapado {ic_indep:+.3f} (n={n_indep} indep)")
        print(f"     COLAS del retorno: skew {sk_r:+.2f}, curtosis(exceso) {ku_r:+.2f}")

    # ============ Bloque 4 — IR alcanzable vs listón ============
    print(f"\n=== Bloque 4 — IR alcanzable vs listón {LISTON}  (IR = IC × √(12 × N_eff_comb={ne_comb:.2f})) ===")
    mult = np.sqrt(12 * ne_comb)
    for name, r in results.items():
        ir = r["ic_indep"] * mult
        irlo, irhi = r["lo"] * mult, r["hi"] * mult
        verdict = ("SUPERA con margen" if irlo > LISTON else "NO despeja" if irhi < LISTON
                   else "INDETERMINADO (banda cruza 0.65)")
        print(f"  [{name}] IR = {r['ic_indep']:+.3f} × {mult:.2f} = {ir:+.2f}  "
              f"(banda [{irlo:+.2f},{irhi:+.2f}]) → {verdict}")


if __name__ == "__main__":
    main()
