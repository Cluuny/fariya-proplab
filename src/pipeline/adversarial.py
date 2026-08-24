"""adversarial.py — Estación 5: revisión adversaria.

Segundo agente, prompt DISTINTO, único trabajo: DESTRUIR la ficha. No resume ni evalúa de
forma balanceada. Razón: los LLM son estructuralmente aduladores hacia el texto que leen; un
revisor que sólo busca fallos contrarresta ese sesgo.

Las ocho preguntas de ataque (cada una devuelve un veredicto por eje). Si CUALQUIER eje
crítico falla, la ficha se rechaza. Las lecciones de H003 (describir≠predecir; benchmark que
comparte exposición) y del OFI (contemporáneo≠predictivo) están codificadas como ejes.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# (clave, pregunta, ¿es crítico? un fallo crítico → reject)
ATTACK_QUESTIONS = [
    ("periodo_descubrimiento", "¿backtest en el mismo período donde se descubrió el efecto?", True),
    ("n_variantes", "¿cuántas variantes probaron antes de reportar ESTA? (multiplicidad)", False),
    ("sesgo_supervivencia", "¿sesgo de supervivencia en el universo?", True),
    ("datos_no_rt", "¿usa datos no disponibles en tiempo real (look-ahead)?", True),
    ("costes_plausibles", "¿costes plausibles para nuestro tamaño y broker?", True),
    ("degradacion_post_pub", "¿evidencia post-publicación de degradación?", False),
    ("contemporaneo_vs_predictivo", "¿el resultado es CONTEMPORÁNEO o PREDICTIVO? (H003/OFI)", True),
    ("benchmark_cero", "¿el benchmark es CERO o comparte la exposición de la estrategia? (H003 beta)", True),
    # AÑADIDOS tras el test ciego (change adversarial-blind-test): el adversario NO detectó
    # espontáneamente la no-independencia autoral (no estaba en la lista y el findings dict no
    # tenía canal para un eje novel). Ahora son ejes explícitos.
    ("autores_independientes", "¿los autores del paper son los mismos del hallazgo original? (independencia de la replicación)", False),
    ("literatura_previa_posterior", "¿existe literatura previa o posterior sobre este mismo efecto, y qué dice?", False),
]
CRITICAL_KEYS = {k for k, _, crit in ATTACK_QUESTIONS if crit}


@dataclass
class AdversarialResult:
    veredicto: str                 # keep | reject
    razon: str
    failed_axes: list[str] = field(default_factory=list)


def evaluate(findings: dict) -> AdversarialResult:
    """`findings` mapea cada clave de ATTACK_QUESTIONS a True (la ficha SUPERA el ataque en ese
    eje) / False (el ataque tuvo éxito, hay un problema). Un eje crítico fallado → reject.

    En producción, el segundo agente (prompt destructor) rellena `findings`; aquí se implementa
    la lógica de compuerta (testeable). Un eje ausente se trata como fallo (conservador: si el
    adversario no pudo descartar el problema, cuenta en contra)."""
    failed = []
    for key, _q, critical in ATTACK_QUESTIONS:
        passed = findings.get(key, False)  # ausente → no superado (conservador)
        if not passed:
            failed.append(key)
    critical_failed = [k for k in failed if k in CRITICAL_KEYS]
    if critical_failed:
        return AdversarialResult(
            veredicto="reject",
            razon=f"falló ejes CRÍTICOS: {critical_failed}",
            failed_axes=failed)
    if failed:
        return AdversarialResult(
            veredicto="keep",
            razon=f"supera los ejes críticos; observaciones no críticas: {failed}",
            failed_axes=failed)
    return AdversarialResult(veredicto="keep", razon="supera los ocho ejes de ataque", failed_axes=[])


def apply(conn, hyp_id: str, findings: dict) -> AdversarialResult:
    from src.pipeline import db

    res = evaluate(findings)
    update = {"id": hyp_id, "adversarial_veredicto": res.veredicto, "adversarial_razon": res.razon}
    if res.veredicto == "reject":
        update["estado"] = "rechazada_por_falsabilidad" if "contemporaneo_vs_predictivo" in res.failed_axes \
            else "rechazada_operabilidad"
    db.upsert(conn, update)
    return res
