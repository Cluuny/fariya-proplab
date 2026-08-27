# Tasks

## 1. Barrido de vol
- [x] 1.1 `scripts/funded_vol_sensitivity.py`: Sharpe {0.3,0.37,0.5} × vol {8,12,15,20,25%} sobre challenge.py
- [x] 1.2 P(pasar), días, P(quemar 4/8/12), payout escalado, P(éxito), EV neto de cuotas por año

## 2. Levantar los tres caveats
- [x] 2.1 (a) supervivencia ACUMULATIVA (camino continuo N×21 d), no independiente
- [x] 2.2 (b) retornos REALES (forma CFD riesgo-igual, colas, estandarizada) además del normal
- [x] 2.3 (c) límite diario INTRADÍA (factor 1.8) — se reporta el efecto por vol

## 3. Entregable + respuesta
- [x] 3.1 `docs/funded_vol_sensitivity.md` D1-D5 + la respuesta en una línea
- [x] 3.2 Decisión Norgate con el cálculo (N_eff 15/38 vs 9-12 comprometido; medido 8.15) → NO
- [x] 3.3 Tests guard; suite verde

## 4. Verificación
- [x] 4.1 Sin datos nuevos/suscripción; sin pre-registro; holdout intacto; optimal_leverage None
