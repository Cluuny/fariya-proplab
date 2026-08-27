# Curva de Sharpe requerido para el ciclo completo de fondeo

## Why

`src/challenge.py` (el simulador de barrera, semana 4) nunca se aplicó a la pregunta que
importa: **¿qué Sharpe mínimo hace falta para pasar el challenge, generar payouts y sobrevivir?**
Es aritmética sobre infraestructura existente — no requiere datos nuevos ni suscripción — y cierra
el programa desde una tercera dirección (el lado del PAYOUT), complementando el suelo de costes y
el cierre por amplitud.

## What Changes

**`scripts/funded_sharpe_requirement.py` + `docs/funded_sharpe_requirement.md`:** barrido sintético
(Sharpe {0,0.2,0.3,0.5,0.8,1.0,1.5} × vol {6,8,10%} × BROKER_MARGIN_MULT {1.0,1.5}) por bootstrap
de bloques a través de `challenge.py`, con la contabilidad de tres resultados (PASA/FALLA/SIN
ABSORBER) y los guards existentes (horizonte insuficiente → nan; optimal_leverage=None). Modelo:
Sharpe BRUTO barrido, neto = bruto − drag de swap DIRECCIONAL (carry ~0 en libro balanceado →
margen unidireccional ×BROKER_MARGIN_MULT×(365/261), no el placeholder unsigned).

- **D1** P(pasar)/P(quemar N=4,8,12)/P(éxito), días, retorno y payout anual sobre $50k split 90%.
- **D2** Sharpe mínimo para P(éxito) ≥ 50/70/80%, donde P(éxito)=P(pasar ambas)×P(sobrevivir 12).
- **D3** aritmética del dinero: payout por Sharpe, cuentas escaladas ($50k→$150k→$300k) para
  $1k/$2.5k mensual, cuotas/año contando quemas.
- **D4** la respuesta en una línea.
- **D5** contraste vs lo medido (H002 0.495, H007-A 0.370, industria 0.32).

**RESULTADO:** requerido ~0.5 (P≥50%, moneda al aire) a ~0.8 (P≥70-80%, ingreso fiable);
lo desplegable (trend 0.37, industria 0.32) queda EN o por DEBAJO de la moneda al aire; H002 0.495
roza el 50% pero no es desplegable (concentración). P(quemar)≈0 → el cuello es PASAR, no sobrevivir.
Coherente con el cierre por amplitud, desde el lado del payout.

## Impact

- NUEVO: `scripts/funded_sharpe_requirement.py`, `docs/funded_sharpe_requirement.md`,
  `tests/test_funded_sharpe_requirement.py` (guards: momentos exactos, monotonía, P(quemar) baja).
- Sin datos nuevos, sin suscripción, sin pre-registro, holdout intacto, optimal_leverage sigue None.
