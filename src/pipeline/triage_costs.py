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


def bruto_requerido(duty_cycle: float, vehiculo: str = "cfd") -> float:
    """Bruto Sharpe requerido para netear `UMBRAL_NETO`, dado el duty y el vehículo."""
    if vehiculo not in VEHICULOS:
        raise ValueError(f"vehículo desconocido: {vehiculo!r} (usa {list(VEHICULOS)})")
    return costs_model.sharpe_bruto_requerido_duty(
        duty_cycle, umbral=UMBRAL_NETO, breakeven_full=VEHICULOS[vehiculo]
    )


@dataclass(frozen=True)
class CostVerdict:
    decision: str                 # keep | reject | requiere_lectura
    razon: str
    requerido_cfd: float
    requerido_futuros: float


def triage_costs(candidate: dict) -> CostVerdict:
    """Evaluar un candidato contra el suelo de costes de AMBOS vehículos.

    Regla:
      - bruto_reportado ausente (None)  → `requiere_lectura` (no se descarta).
      - bruto_reportado > requerido en AL MENOS un vehículo → `keep`.
      - bruto_reportado <= requerido en ambos → `reject`.

    `duty_cycle_estimado` es obligatorio; sin él no hay listón. `turnover_estimado` se
    conserva en la ficha para el registro de aprendizaje pero no entra en el listón por
    duty (ese ya está calibrado sobre las corridas reales).
    """
    duty = candidate.get("duty_cycle_estimado")
    if duty is None:
        raise ValueError("triage_costs requiere duty_cycle_estimado")
    req_cfd = bruto_requerido(duty, "cfd")
    req_fut = bruto_requerido(duty, "futures")

    reportado = candidate.get("bruto_reportado")
    if reportado is None:
        return CostVerdict(
            decision="requiere_lectura",
            razon="el abstract no reporta bruto; baja prioridad, pendiente de lectura",
            requerido_cfd=req_cfd,
            requerido_futuros=req_fut,
        )

    pasa_cfd = reportado > req_cfd
    pasa_fut = reportado > req_fut
    if pasa_cfd or pasa_fut:
        vh = "CFD y futuros" if (pasa_cfd and pasa_fut) else ("CFD" if pasa_cfd else "futuros")
        return CostVerdict(
            decision="keep",
            razon=f"bruto {reportado:.2f} supera el requerido en {vh} "
                  f"(cfd {req_cfd:.2f}, fut {req_fut:.2f})",
            requerido_cfd=req_cfd,
            requerido_futuros=req_fut,
        )
    return CostVerdict(
        decision="reject",
        razon=f"bruto {reportado:.2f} < requerido en ambos vehículos "
              f"(cfd {req_cfd:.2f}, fut {req_fut:.2f})",
        requerido_cfd=req_cfd,
        requerido_futuros=req_fut,
    )


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
        "triage_costo": verdict.decision,
        "triage_costo_razon": verdict.razon,
        "estado": estado,
    })
    return verdict
