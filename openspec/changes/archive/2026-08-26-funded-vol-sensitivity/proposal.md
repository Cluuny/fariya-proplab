# Sensibilidad del ciclo de fondeo a la volatilidad objetivo

## Why

`funded_sharpe_requirement` halló P(quemar)≈0 y concluyó «el cuello es PASAR, no sobrevivir»,
poniendo en duda la restricción de vol al 8% (§2.1). Pero ese hallazgo sólo barrió vol 6-10% con
un modelo de supervivencia INDEPENDIENTE (optimista). Hay que barrer hasta vol alta con los tres
caveats que yo mismo registré levantados, y responder: ¿existe una vol a la que un Sharpe 0.37 —lo
alcanzable— genere payouts materialmente mayores sin que la barrera muerda?

## What Changes

**`scripts/funded_vol_sensitivity.py` + `docs/funded_vol_sensitivity.md`:** barrido Sharpe
{0.3,0.37,0.5} × vol {8,12,15,20,25%} sobre `challenge.py`, con los tres caveats LEVANTADOS:
- **(a)** supervivencia ACUMULATIVA (camino continuo N×21 días, drawdown estático acumulado desde
  el inicio), no independiente (p^N). Sólo esto sube la quema a 8% de ~0 a ~0.15.
- **(b)** retornos REALES (forma de cartera CFD riesgo-igual, curtosis ~3.2, estandarizada al
  objetivo, bootstrap de bloques) además del sintético normal.
- **(c)** límite diario INTRADÍA (factor 1.8 sobre el movimiento diario) — dominante a vol alta.

Reporta P(pasar), días, P(quemar 4/8/12), payout escalado, P(éxito), y VALOR ESPERADO NETO DE
CUOTAS por año (la métrica de decisión).

**RESULTADO:** el modelo normal ingenuo dice que subir la vol MEJORA el EV; los tres caveats lo
INVIERTEN — la barrera muerde catastróficamente por encima de ~12% (a 15% burn12 0.83, a 20% 0.97)
y el EV cae a negativo. El óptimo sigue siendo ~8%. **La restricción de vol de §2.1 queda
vindicada, no invalidada.** Respuesta: NO existe una vol alta que rescate a Sharpe 0.37.

**Decisión Norgate (con el cálculo):** cerrar 0.37→0.50 por amplitud exige N_eff ≈ 15, a 0.80 ≈ 38
(Sharpe ∝ √N_eff desde el ancla de futuros 8.15); la expectativa era 9-12, el medido 8.15 → los
$50/mes compran N_eff ~8, no cierran el hueco. NO se contrata.

## Impact

- NUEVO: `scripts/funded_vol_sensitivity.py`, `docs/funded_vol_sensitivity.md`,
  `tests/test_funded_vol_sensitivity.py` (supervivencia baja con vol, intradía aumenta quema,
  acumulativa muerde a 8%, forma real con colas).
- Sin datos nuevos ni suscripción; sin pre-registro; holdout intacto; optimal_leverage sigue None.
