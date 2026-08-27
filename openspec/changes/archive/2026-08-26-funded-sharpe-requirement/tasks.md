# Tasks

## 1. Barrido (D1)
- [x] 1.1 `scripts/funded_sharpe_requirement.py`: sintético S×vol×mult por bootstrap de bloques vía challenge.py
- [x] 1.2 P(pasar 1/2), P cond, días, P(quemar N=4/8/12), retorno y payout anual sobre $50k split 90%
- [x] 1.3 Guards respetados: horizonte insuficiente→nan, optimal_leverage=None, swap direccional (no unsigned), BROKER_MARGIN_MULT {1.0,1.5}

## 2. Ciclo completo (D2)
- [x] 2.1 P(éxito)=P(pasar ambas)×P(sobrevivir 12); Sharpe mínimo para ≥50/70/80%

## 3. Aritmética del dinero (D3)
- [x] 3.1 Payout por Sharpe, escalado $50k→$150k→$300k, cuentas para $1k/$2.5k mensual, cuotas/año con quemas

## 4. Entregable
- [x] 4.1 `docs/funded_sharpe_requirement.md` D1-D5 + la respuesta en una línea (D4) + contraste vs medido (D5)
- [x] 4.2 Tests guard (momentos exactos, monotonía de P(éxito), P(quemar) baja); suite verde

## 5. Verificación
- [x] 5.1 Sin datos nuevos/suscripción; sin pre-registro; holdout intacto; optimal_leverage sigue None
