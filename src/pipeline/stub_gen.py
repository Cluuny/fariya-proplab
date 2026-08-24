"""stub_gen.py — Estación 6: generación de stub en signals.py.

Una ficha aprobada genera una función en `signals.py` con el CONTRATO FIJO (precios → pesos).
El motor NO cambia. El stub es un esqueleto con la regla documentada y un NotImplementedError:
obliga a implementar la señal a mano contra el contrato, no la inventa el LLM.
"""

from __future__ import annotations

import re


def _fn_name(hyp_id: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", str(hyp_id).lower()).strip("_")
    return f"signal_{slug}"


def generate_stub(ficha: dict) -> str:
    """Devuelve el código fuente del stub para una ficha aprobada. Contrato:
    `def signal_<id>(prices: pd.DataFrame) -> pd.DataFrame:  # devuelve pesos alineados`."""
    name = _fn_name(ficha["id"])
    hip = (ficha.get("hipotesis") or "").strip().replace("\n", " ")
    entrada = (ficha.get("regla_entrada") or "").strip().replace("\n", " ")
    salida = (ficha.get("regla_salida") or "").strip().replace("\n", " ")
    fals = (ficha.get("falsador") or "").strip().replace("\n", " ")
    clase = ficha.get("clase_de_dato", "?")
    fuente = ficha.get("url") or ficha.get("fuente", "?")
    return f'''def {name}(prices: pd.DataFrame) -> pd.DataFrame:
    """{ficha.get('id')} — {ficha.get('titulo','').strip()}

    Hipótesis: {hip}
    Regla de entrada: {entrada}
    Regla de salida: {salida}
    Clase de dato: {clase} · fuente: {fuente}
    FALSADOR (pre-registrado): {fals}

    Contrato: recibe precios (columnas = instrumentos), devuelve PESOS alineados
    (mismas columnas/índice). El motor (engine.backtest) aplica costes; NO se toca.
    """
    raise NotImplementedError(
        "stub generado por el pipeline (estación 6). Implementar la señal a mano contra "
        "el contrato precios→pesos; el LLM NO la inventa.")
'''


def append_to_signals(ficha: dict, path: str = "src/signals.py") -> str:
    """Anexa el stub a signals.py (idempotente: no duplica si ya existe la función)."""
    from pathlib import Path

    name = _fn_name(ficha["id"])
    p = Path(path)
    src = p.read_text() if p.exists() else ""
    if f"def {name}(" in src:
        return name  # ya existe
    stub = generate_stub(ficha)
    p.write_text(src.rstrip() + "\n\n\n" + stub)
    return name
