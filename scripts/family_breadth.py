"""family_breadth.py — ¿son descorrelacionadas las familias? (Bloque 2 de pre-run-003-calibration).

Todo el plan se apoya en 0.4·√4 = 0.8, y ese √4 EXIGE cuatro estrategias DESCORRELACIONADAS — nunca
medido. Se generan las series de retorno diario NETO de tres familias (trend, carry, estacionalidad)
con el motor real, se mide su matriz de correlación sobre la ventana común, y se calcula el N_eff
de ESTRATEGIAS (mismo participation ratio que se usó para instrumentos). El multiplicador real es
√(N_eff estrategias), no √4.

Carry: H002 se cribó sin señal de producción; aquí se construye un PROXY de carry (signo del
diferencial de tasas histórico × inverse-vol, misma maquinaria de sizing que tsmom/tom) — etiquetado
como proxy para la MEDICIÓN, no una señal pre-registrada.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src import config, engine, rates, signals

FX = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURJPY", "GBPJPY", "AUDJPY", "EURAUD"]
IDX = ["SPX500", "GER40", "JPN225", "HK50"]
TREND_UNIV = list(config.INSTRUMENTS)  # los 17 (H007)


def _prices(cols):
    return pd.DataFrame({c: pd.read_parquet(config.DATA_CLEAN / f"{c}.parquet")["close"] for c in cols})


def carry_weights(prices, *, vol_window=63, vol_target=0.08, max_gross=config.MAX_GROSS_EXPOSURE):
    """Pesos de carry: long carry positivo / short negativo, inverse-vol, escalado ex-ante a vol_target."""
    carry = rates.carry_matrix(prices.index, list(prices.columns))
    sign = np.sign(carry).reindex(index=prices.index, columns=prices.columns).fillna(0.0)
    vol = engine.rolling_vol(prices, vol_window)
    invvol = (1.0 / vol.replace(0.0, np.nan)).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    raw = sign * invvol
    gross_raw = raw.abs().sum(axis=1)
    rel = raw.div(gross_raw.where(gross_raw > 0, np.nan), axis=0).fillna(0.0)
    asset_ret = engine._asset_returns(prices)
    port_ret = (rel.shift(1).fillna(0.0) * asset_ret).sum(axis=1)
    ann = np.sqrt(config.TRADING_DAYS_PER_YEAR)
    port_vol = (port_ret.rolling(vol_window).std() * ann).shift(1)
    scalar = (vol_target / port_vol).replace([np.inf, -np.inf], np.nan)
    w = rel.mul(scalar, axis=0)
    gross = w.abs().sum(axis=1)
    over = gross > max_gross
    if over.any():
        clip = pd.Series(1.0, index=w.index)
        clip[over] = max_gross / gross[over]
        w = w.mul(clip, axis=0)
    return w.fillna(0.0)


def n_eff(corr: np.ndarray) -> float:
    ev = np.linalg.eigvalsh(corr)
    ev = ev[ev > 0]
    return float((ev.sum() ** 2) / (ev ** 2).sum())


def main():
    # series de retorno NETO por familia (portfolio-level)
    ptr = _prices(TREND_UNIV)
    trend = engine.backtest(ptr, signals.tsmom(ptr, lookback_months=12))
    pidx = _prices(IDX)
    tom = engine.backtest(pidx, signals.tom_seasonal(pidx))
    pfx = _prices(FX)
    carry = engine.backtest(pfx, carry_weights(pfx))

    df = pd.DataFrame({"trend": trend, "carry": carry, "estacionalidad": tom}).dropna(how="any")
    # sólo días con actividad de las tres (tom está flat la mayor parte del mes → usar solape real)
    df = df.loc[(df != 0).any(axis=1)]
    print(f"Ventana común: {df.index.min().date()} → {df.index.max().date()}  ({len(df)} días)")
    print(f"Sharpe individual (neto, en la ventana común):")
    for c in df.columns:
        s = df[c]
        print(f"  {c:16s} {engine.sharpe(s):+.2f}   vol {s.std()*np.sqrt(252)*100:.1f}%")

    corr = df.corr()
    print("\nMatriz de correlación (retornos diarios netos):")
    print(corr.round(2).to_string())

    ne = n_eff(corr.to_numpy())
    iu = np.triu_indices(len(corr), 1)
    pair = corr.to_numpy()[iu]
    print(f"\nCorrelación par a par: " + " · ".join(
        f"{corr.columns[i]}-{corr.columns[j]} {corr.iloc[i,j]:+.2f}"
        for i, j in zip(*iu)))
    print(f"\nN_eff de ESTRATEGIAS = {ne:.2f}  (de 3 familias; ideal 3)")
    print(f"Multiplicador REAL sobre el Sharpe = √N_eff = {ne**0.5:.2f}  (vs √3 = {3**0.5:.2f} si fueran independientes)")
    # ¿qué Sharpe individual haría falta para 0.8?  0.8 = S · √N_eff  → S = 0.8/√N_eff
    # extrapolado a 4 familias con la MISMA correlación media (MISMO participation ratio,
    # autovalores de 4 equicorrelacionadas a rho: 1+3rho una vez, 1-rho tres veces).
    rho_bar = float(pair.mean())
    ne4 = 16.0 / ((1 + 3 * rho_bar) ** 2 + 3 * (1 - rho_bar) ** 2)  # participation ratio, N=4
    print(f"\nCorrelación media entre familias: {rho_bar:+.2f}")
    print(f"Para el objetivo 0.8 con las 3 familias medidas: Sharpe individual = 0.8/√{ne:.2f} = {0.8/ne**0.5:.2f}")
    print(f"Extrapolado a 4 familias a esa correlación media (N_eff participation ≈ {ne4:.2f}): "
          f"Sharpe individual = 0.8/√{ne4:.2f} = {0.8/ne4**0.5:.2f}")


if __name__ == "__main__":
    main()
