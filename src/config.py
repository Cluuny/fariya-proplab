"""Configuración explícita y versionada del laboratorio (decisión D6).

Todo lo que afecta un resultado medido vive aquí, no incrustado ad hoc en el
código, para que los backtests sean reproducibles y ajustables.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# --- Rutas ---
ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT / "data" / "raw"
DATA_CLEAN = ROOT / "data" / "clean"
RESULTS = ROOT / "results"

# --- Universo (documento maestro, sección 8.2) ---
INSTRUMENTS: tuple[str, ...] = (
    "EURUSD",
    "GBPUSD",
    "USDJPY",
    "AUDUSD",
    "USDCAD",
    "XAUUSD",
    "SPX500",
    "NAS100",
    "GER40",
    "UK100",
)

# --- Validación de calidad de datos ---
# Umbral de retorno anómalo, en desviaciones estándar (documento: >5σ).
ANOMALOUS_RETURN_SIGMA = 5.0


@dataclass(frozen=True)
class CostModel:
    """Costos de operar un instrumento. Aplicados SOLO por engine.py.

    Todos en fracción del notional operado (p. ej. 0.0001 = 1 bp), salvo
    ``commission_per_unit`` que es por unidad de peso rotado.
    """

    spread: float = 0.0001          # medio spread efectivo por lado
    slippage: float = 0.00005       # deslizamiento por lado
    impact: float = 0.0             # impacto de mercado por unidad rotada
    commission: float = 0.0         # comisión por unidad rotada


# Modelo de costos por defecto y overrides por instrumento.
DEFAULT_COST = CostModel()
COSTS: dict[str, CostModel] = {sym: DEFAULT_COST for sym in INSTRUMENTS}


@dataclass(frozen=True)
class SharpeReference:
    """Sharpe histórico conocido de referencia para verificar el motor.

    La verificación se expresa como tolerancia, no igualdad exacta, y la
    fuente/ventana se fijan aquí para que el test sea reproducible.
    """

    instrument: str
    value: float
    window: str          # p. ej. "2005-2023"
    source: str          # de dónde viene el número de referencia
    tolerance: float     # tolerancia absoluta admitida en el Sharpe


# Referencia por defecto para el test de verificación de engine.py.
# NOTA: el valor concreto se fija al disponer del dato histórico real; el test
# de aceptación lee esta estructura.
SHARPE_REFERENCE = SharpeReference(
    instrument="SPX500",
    value=0.0,
    window="2005-2023",
    source="TBD — fijar con serie histórica real (ver task 4.4)",
    tolerance=0.15,
)

# Días de trading al año, para anualizar Sharpe.
TRADING_DAYS_PER_YEAR = 252
