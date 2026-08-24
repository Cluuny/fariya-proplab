"""triage_costs.py — Estación 3: el triaje de COSTOS (el filtro nuevo).

Aritmética pura, reutiliza `costs_model.sharpe_bruto_requerido_duty`. Va ANTES de leer
el paper porque es el filtro que MÁS mata (H005 y H006 murieron sin correrse, por
aritmética) y es más barato y más discriminante que la revisión adversaria.

Cada candidato declara, ESTIMADO DEL ABSTRACT (no del paper completo):
  - duty_cycle_estimado   (fracción del tiempo en mercado)
  - turnover_estimado     (rotaciones/año; se guarda para el registro, no decide aquí)
  - bruto_reportado       (Sharpe bruto que dice la literatura, si lo dice)

El sistema calcula el bruto requerido y rechaza si el reportado no lo supera. Si el
abstract NO reporta bruto, marca `requiere_lectura` (no rechaza; baja prioridad).

Parametrizado por VEHÍCULO: el requerido con CFD (0.64 a duty 100%) y con futuros (0.42)
son distintos porque el suelo de costes es distinto (margen diario del CFD vs. sin margen
en futuros). El pipeline evalúa contra AMBOS.
"""

from __future__ import annotations

from dataclasses import dataclass

from src import costs_model

# Vehículo → break-even a duty completo (el `breakeven_full` de sharpe_bruto_requerido_duty).
# CFD: margen diario domina → break-even 0.24 → requerido 0.64 a duty 100%.
# Futuros: sin margen diario → break-even ~0.024 → requerido ~0.424 a duty 100%.
# (docs/cost_floor.md, docs/futures_case.md.)
VEHICULOS = {
    "cfd": 0.24,
    "futures": 0.024,
}
UMBRAL_NETO = 0.40  # el net Sharpe objetivo (metrica_exito del proyecto)

# Listones MEDIDOS de referencia (bruto requerido), recalibrados con ambos ciclos.
# Se usan para reportar contra qué se compara cada candidato (docs/program_verdict.md,
# docs/cost_floor.md, docs/own_capital_phase.md).
LISTONES_REFERENCIA = {
    "cfd_swing_8pct":        0.64,   # CFD spot, 8% vol
    "futuros_swing_8pct":    0.42,
    "cripto_perp_mejor":     0.65,   # maker + 1 rt/día + funding evitado (vol real ~60%)
    "capital_propio_20pct":  0.50,   # SÓLO si la vol extra viene de instrumentos más volátiles
                                     # al mismo notional, NO de apalancamiento (coste/vol
                                     # invariante — verificado). Ver own_capital_phase.md.
}


def sharpe_activo_requerido(duty_cycle: float) -> float:
    """Duty bajo: el Sharpe ACTIVO requerido SUBE, no baja: 0.40/√duty + 0.245.
    Reexportado de costs_model para el triaje (lección del ciclo CFD)."""
    return costs_model.sharpe_activo_requerido(duty_cycle)


def bruto_requerido(duty_cycle: float, vehiculo: str = "cfd") -> float:
    """Bruto Sharpe requerido para netear `UMBRAL_NETO`, dado el duty y el vehículo."""
    if vehiculo not in VEHICULOS:
        raise ValueError(f"vehículo desconocido: {vehiculo!r} (usa {list(VEHICULOS)})")
    return costs_model.sharpe_bruto_requerido_duty(
        duty_cycle, umbral=UMBRAL_NETO, breakeven_full=VEHICULOS[vehiculo]
    )


_INTRADAY_FREQ = {"intraday_bar", "tick", "orderbook"}


@dataclass(frozen=True)
class CostVerdict:
    decision: str                 # keep | reject | requiere_lectura
    razon: str
    requerido_cfd: float
    requerido_futuros: float
    requerido_intraday: float | None = None  # sólo en régimen intradía


def triage_costs(candidate: dict) -> CostVerdict:
    """Evaluar un candidato contra el suelo de costes correcto para su FRECUENCIA.

    - EOD (swing): contra AMBOS vehículos (CFD 0.64 / futuros 0.424) por duty.
    - intradía/tick/orderbook: contra el suelo por ROTACIÓN (`trades_por_dia_estimado`,
      `contrato_ref`), donde el coste lo domina rotar, no mantener.

    Regla común:
      - bruto_reportado ausente (None)  → `requiere_lectura` (no se descarta).
      - bruto_reportado > requerido      → `keep`.
      - bruto_reportado <= requerido     → `reject`.
    """
    freq = candidate.get("frecuencia") or "EOD"
    if freq in _INTRADAY_FREQ:
        return _triage_intraday(candidate)

    duty = candidate.get("duty_cycle_estimado")
    if duty is None:
        raise ValueError("triage_costs (EOD) requiere duty_cycle_estimado")
    req_cfd = bruto_requerido(duty, "cfd")
    req_fut = bruto_requerido(duty, "futures")

    reportado = candidate.get("bruto_reportado")
    if reportado is None:
        return CostVerdict("requiere_lectura",
                           "el abstract no reporta bruto; baja prioridad, pendiente de lectura",
                           req_cfd, req_fut)

    pasa_cfd, pasa_fut = reportado > req_cfd, reportado > req_fut
    if pasa_cfd or pasa_fut:
        vh = "CFD y futuros" if (pasa_cfd and pasa_fut) else ("CFD" if pasa_cfd else "futuros")
        return CostVerdict("keep",
                           f"bruto {reportado:.2f} supera el requerido en {vh} "
                           f"(cfd {req_cfd:.2f}, fut {req_fut:.2f})", req_cfd, req_fut)
    return CostVerdict("reject",
                       f"bruto {reportado:.2f} < requerido en ambos vehículos "
                       f"(cfd {req_cfd:.2f}, fut {req_fut:.2f})", req_cfd, req_fut)


def _triage_intraday(candidate: dict) -> CostVerdict:
    trades = candidate.get("trades_por_dia_estimado")
    if trades is None:
        raise ValueError("triage_costs (intradía) requiere trades_por_dia_estimado")
    contrato = candidate.get("contrato_ref") or "ES"
    req_id = costs_model.sharpe_bruto_requerido_intraday(trades, contrato)
    # referencias swing (para el contraste en la razón)
    req_cfd, req_fut = bruto_requerido(1.0, "cfd"), bruto_requerido(1.0, "futures")
    reportado = candidate.get("bruto_reportado")
    if reportado is None:
        return CostVerdict("requiere_lectura",
                           f"intradía {contrato} {trades}/día: sin bruto reportado; "
                           f"requerido {req_id:.2f}, pendiente de lectura",
                           req_cfd, req_fut, requerido_intraday=req_id)
    if reportado > req_id:
        return CostVerdict("keep",
                           f"bruto {reportado:.2f} supera el requerido intradía "
                           f"{req_id:.2f} ({contrato}, {trades}/día)",
                           req_cfd, req_fut, requerido_intraday=req_id)
    return CostVerdict("reject",
                       f"bruto {reportado:.2f} < requerido intradía {req_id:.2f} "
                       f"({contrato}, {trades}/día — lo domina rotar)",
                       req_cfd, req_fut, requerido_intraday=req_id)


def apply(conn, hyp_id: str, candidate: dict | None = None) -> CostVerdict:
    """Correr el triaje de costos sobre una fila de la DB y persistir el resultado."""
    from src.pipeline import db

    row = candidate or db.get(conn, hyp_id)
    if row is None:
        raise KeyError(hyp_id)
    verdict = triage_costs(row)
    estado = {
        "keep": "en_cola",
        "reject": "rechazada_costo",
        "requiere_lectura": "requiere_lectura",
    }[verdict.decision]
    db.upsert(conn, {
        "id": hyp_id,
        "bruto_requerido_cfd": verdict.requerido_cfd,
        "bruto_requerido_futuros": verdict.requerido_futuros,
        "bruto_requerido_intraday": verdict.requerido_intraday,
        "triage_costo": verdict.decision,
        "triage_costo_razon": verdict.razon,
        "estado": estado,
    })
    return verdict
