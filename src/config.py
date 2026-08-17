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


# --- Reglas de la firma de fondeo (parametrizadas; NO hardcodear una firma) ---
@dataclass(frozen=True)
class FirmRules:
    """Reglas de un challenge de cuenta de fondeo.

    Todas las magnitudes de barrera se expresan como FRACCIÓN del capital
    inicial (p. ej. 0.10 = 10%). El drawdown es ESTÁTICO (contra capital
    inicial, no trailing — documento maestro sección 2.2).
    """

    phase1_target: float = 0.10        # objetivo fase 1 (+10%)
    phase2_target: float = 0.05        # objetivo fase 2 (+5%)
    daily_loss_limit: float = 0.05     # límite de pérdida diaria (5%)
    max_drawdown: float = 0.10         # drawdown máximo estático (10%)
    n_payouts: int = 4                 # nº de payouts N para "quemar cuenta"
    fee: float = 500.0                 # costo de la cuota del challenge (USD)
    payout_per_cycle: float = 1000.0   # payout esperado por ciclo tras fondeo (USD)


DEFAULT_FIRM_RULES = FirmRules()


# --- Parámetros del simulador de barrera (challenge.py) ---
@dataclass(frozen=True)
class SimulatorParams:
    """Configuración del simulador de barrera por block bootstrap."""

    block_size: int = 20               # tamaño de bloque (>1; ~1 mes de trading)
    n_bootstraps: int = 10_000         # nº de trayectorias simuladas
    horizon_days: int = 252            # horizonte máximo por fase (días)
    seed: int = 12345                  # semilla para reproducibilidad
    # Malla de apalancamiento: multiplicadores k evaluados para la curva P(pasar).
    leverage_min: float = 0.25
    leverage_max: float = 3.0
    leverage_step: float = 0.25


DEFAULT_SIM_PARAMS = SimulatorParams()
