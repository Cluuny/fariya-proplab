"""challenge.py — Simulador de barrera (EL NÚCLEO diferenciador).

FUERA DE ALCANCE en este change (Bloque A). Se implementa en el Bloque B.

Contrato previsto: toma los retornos diarios netos de una estrategia, corre
~10.000 bootstraps POR BLOQUES (no i.i.d. — preserva autocorrelación y
clustering de volatilidad) y aplica las reglas exactas de la firma de fondeo
para devolver:

    - P(pasar fase 1), P(pasar fase 2), P(pasar ambas)
    - Días esperados hasta pasar
    - P(quemar la cuenta fondeada antes del payout N)
    - Valor esperado neto de cuotas  ← la métrica que realmente decide
    - Curva P(pasar) frente a apalancamiento → multiplicador óptimo

Aceptación (Bloque B): con retornos sintéticos de deriva cero devuelve P≈50%
para barreras 10/10, validado contra la fórmula analítica cerrada de primer
paso con doble barrera.
"""

from __future__ import annotations


def simulate_challenge(*args, **kwargs):
    raise NotImplementedError(
        "challenge.py es Bloque B (fuera de alcance de este change)."
    )
