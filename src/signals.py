"""signals.py — Contrato de señal (la frontera con el Flujo 2).

Una señal es una FUNCIÓN PURA: recibe precios (y opcionalmente parámetros) y
devuelve un DataFrame de pesos objetivo indexado por fecha, una columna por
instrumento. Sin estado, sin I/O, sin mutar entradas; determinista.

Invariante de exposición: en cada fecha, sum(|pesos|) <= 1.

Este contrato es lo que permite que el futuro Flujo 2 genere código que encaje
directamente en el motor. Cada estrategia es ~20 líneas y testeable en aislamiento.
"""

from __future__ import annotations

from typing import Protocol

import pandas as pd

# Tolerancia numérica para el invariante de exposición.
_EXPOSURE_TOL = 1e-9


class Signal(Protocol):
    """Contrato de una función de señal pura."""

    def __call__(self, prices: pd.DataFrame, /, **params) -> pd.DataFrame:
        """precios -> pesos objetivo (índice = fechas, columnas = instrumentos)."""
        ...


def check_exposure(weights: pd.DataFrame, tol: float = _EXPOSURE_TOL) -> pd.Index:
    """Devuelve las fechas donde sum(|pesos|) excede 1 (vacío si conforme)."""
    gross = weights.abs().sum(axis=1)
    return weights.index[gross > 1 + tol]


def validate_weights(weights: pd.DataFrame, tol: float = _EXPOSURE_TOL) -> None:
    """Valida el invariante de exposición; lanza ValueError si se viola."""
    bad = check_exposure(weights, tol)
    if len(bad):
        raise ValueError(
            f"Exposición > 1 en {len(bad)} fecha(s): {list(bad[:5])}"
            + (" …" if len(bad) > 5 else "")
        )


def buy_and_hold(prices: pd.DataFrame, /, *, weight: float = 1.0) -> pd.DataFrame:
    """Señal de referencia: exposición constante, repartida entre instrumentos.

    Función pura conforme al contrato: mantiene `weight` de exposición bruta
    total, dividida en partes iguales entre las columnas de `prices`, constante
    en el tiempo. No muta `prices`.
    """
    n = prices.shape[1]
    if n == 0:
        return pd.DataFrame(index=prices.index.copy())
    per = weight / n
    weights = pd.DataFrame(per, index=prices.index.copy(), columns=list(prices.columns))
    return weights
