"""cost_model.py — Bloque 3: modelo de costes cripto (Binance USDⓈ-M perpetuos).

Tres componentes, con precios VERIFICADOS de la tabla pública de Binance Futures
(binance.com/en/fee/futureFee, consulta 2026-08-24):

  (3.1) COMISIÓN, con distinción MAKER vs TAKER. VIP0: maker 0.02%, taker 0.05%. Es la
        MITAD del problema económico: proveer liquidez (maker) paga menos de la mitad que
        cruzar el spread (taker). Se parametriza `fraccion_maker`.
  (3.2) FUNDING. Cada 8 h en cortes FIJOS 00:00/08:00/16:00 UTC. Normal ~0.01%/período
        (~11%/año si se mantiene); hasta ~0.1% en alta volatilidad. CLAVE: es EVITABLE —
        un day trader que cierra antes de los cortes paga CERO. Se modela como función de
        si la posición está abierta en el corte, NO como cargo diario continuo. Es la
        PRIMERA estructura de costes del proyecto que PREMIA estar FUERA del mercado.
  (3.3) SLIPPAGE. Se estima del propio libro (spread + profundidad vs tamaño de orden), no
        se asume. Para BTCUSDT el spread medido es ~0.03 bp (top of book de 1 tick): para
        tamaños que caben en el mejor nivel el slippage es despreciable frente a la
        comisión; órdenes que barren el libro añaden slippage a MEDIR por estrategia.

Diferencia estructural con futuros: cripto opera 24/7 → **365 días/año**, no 252.

Nota de comparabilidad: el suelo requerido se calcula sobre la VOL REAL del instrumento
(BTC ~60%/año, medido 2024-01-02), no sobre un objetivo de 8%. Ésa es la base correcta
"por unidad de riesgo"; las referencias CFD 0.64 / MES 0.85 del proyecto se calcularon con
la convención simplificada de 8% y NO son directamente comparables en nivel absoluto — el
número comparable entre vehículos es el COSTE POR UNIDAD DE RIESGO (ver docs/crypto_pivot.md).
"""

from __future__ import annotations

from dataclasses import dataclass

# --- (3.1) comisiones VIP0, verificadas (binance.com/en/fee/futureFee, 2026-08-24) ---
MAKER_FEE = 0.0002   # 0.02%
TAKER_FEE = 0.0005   # 0.05%

# --- (3.2) funding ---
FUNDING_TIMES_UTC = (0, 8, 16)          # cortes fijos
FUNDING_INTERVALS_PER_DAY = 3
FUNDING_PER_INTERVAL_DEFAULT = 0.0001   # 0.01%/período (~11%/año si se mantiene siempre)

# --- calendario y vol de referencia (BTC, medido 2024-01-02; la vol real varía) ---
CRYPTO_TRADING_DAYS = 365
VOL_ANUAL_BTC = 0.60      # anualizada (1-min × √(1440·365)); medido 0.597
VOL_DIARIA_BTC = 0.031    # vol diaria realizada medida (3.1%)
UMBRAL_NETO = 0.40

# slippage por round-trip: piso = el spread medido (~0.03 bp); órdenes grandes barren libro
SLIPPAGE_RT_DEFAULT = 0.0000034   # 0.034 bp (spread medido BTCUSDT 2024-01-02)


def comision_round_trip(fraccion_maker: float) -> float:
    """Comisión por round-trip (entrada+salida) mezclando maker/taker.
    fraccion_maker=1 → 2·maker; =0 → 2·taker."""
    if not 0.0 <= fraccion_maker <= 1.0:
        raise ValueError("fraccion_maker debe estar en [0, 1]")
    por_fill = fraccion_maker * MAKER_FEE + (1 - fraccion_maker) * TAKER_FEE
    return 2.0 * por_fill


def coste_por_unidad_riesgo(fraccion_maker: float = 0.0, *,
                            vol_diaria: float = VOL_DIARIA_BTC) -> float:
    """El número del PIVOTE: comisión round-trip / vol diaria. BTC taker ≈ 0.033
    (reproduce la razón del pivote); maker ≈ 0.013. MES ~0.063 (dato del pivote)."""
    return comision_round_trip(fraccion_maker) / vol_diaria


def funding_anual(cruces_por_dia: int, *, funding_rate: float = FUNDING_PER_INTERVAL_DEFAULT) -> float:
    """Coste de funding anual = cruces_por_día · 365 · tasa. EVITABLE: cruces=0 → 0.
    Una posición mantenida cruza los 3 cortes/día; un day trader que cierra antes → 0."""
    if not 0 <= cruces_por_dia <= FUNDING_INTERVALS_PER_DAY:
        raise ValueError(f"cruces_por_dia en [0, {FUNDING_INTERVALS_PER_DAY}]")
    return cruces_por_dia * CRYPTO_TRADING_DAYS * funding_rate


@dataclass(frozen=True)
class CryptoCostBreakdown:
    comision: float      # %/año por comisión (rotación)
    slippage: float      # %/año por slippage (rotación)
    funding: float       # %/año por funding (EVITABLE)
    total: float


def costo_anual_cripto(trades_por_dia: float, *, fraccion_maker: float = 0.0,
                       cruces_funding_por_dia: int = 0,
                       slippage_rt: float = SLIPPAGE_RT_DEFAULT,
                       funding_rate: float = FUNDING_PER_INTERVAL_DEFAULT) -> CryptoCostBreakdown:
    """Coste anual (fracción del notional). Rotación (comisión+slippage) × 365 + funding."""
    rot = trades_por_dia * CRYPTO_TRADING_DAYS
    comision = rot * comision_round_trip(fraccion_maker)
    slippage = rot * slippage_rt
    funding = funding_anual(cruces_funding_por_dia, funding_rate=funding_rate)
    return CryptoCostBreakdown(comision, slippage, funding, comision + slippage + funding)


def sharpe_bruto_requerido_cripto(trades_por_dia: float, *, fraccion_maker: float = 0.0,
                                  cruces_funding_por_dia: int = 0,
                                  vol_anual: float = VOL_ANUAL_BTC,
                                  slippage_rt: float = SLIPPAGE_RT_DEFAULT,
                                  funding_rate: float = FUNDING_PER_INTERVAL_DEFAULT,
                                  umbral: float = UMBRAL_NETO) -> float:
    """Bruto Sharpe requerido para netear `umbral`, sobre la VOL REAL del instrumento.

        requerido = umbral + costo_anual / vol_anual
    """
    costo = costo_anual_cripto(trades_por_dia, fraccion_maker=fraccion_maker,
                               cruces_funding_por_dia=cruces_funding_por_dia,
                               slippage_rt=slippage_rt, funding_rate=funding_rate).total
    return umbral + costo / vol_anual


def tabla_requerido(trades=(1, 2, 5, 10), makers=(0.0, 0.5, 1.0), **kw) -> list[dict]:
    """Genera el entregable: requerido cruzado por round-trips × fracción maker × funding
    (posición abierta en corte: no=0 cruces / sí=3 cruces)."""
    rows = []
    for t in trades:
        for fm in makers:
            for cruces, etiqueta in ((0, "no"), (FUNDING_INTERVALS_PER_DAY, "sí")):
                req = sharpe_bruto_requerido_cripto(
                    t, fraccion_maker=fm, cruces_funding_por_dia=cruces, **kw)
                rows.append({"trades_dia": t, "fraccion_maker": fm,
                             "funding_en_corte": etiqueta, "bruto_requerido": req})
    return rows
