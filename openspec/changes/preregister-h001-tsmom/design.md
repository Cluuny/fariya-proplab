## Context

Ver `proposal.md`. Este change escribe un único artefacto de texto (`hypotheses/H001_tsmom.yaml`) siguiendo el esquema de ficha §7.1 del documento maestro. No hay código ni spec. Las decisiones de contenido ya se tomaron con el usuario.

## Goals / Non-Goals

**Goals:** una ficha de pre-registro completa, con el FALSADOR y la regla testeable, que sirva de contrato para la implementación posterior.

**Non-Goals:** implementar TSMOM, correr backtests, elegir el apalancamiento (diferido). No editar el falsador después.

## Decisions (contenido de la ficha)

### D1 — Universo adaptado: 9 instrumentos, no 58 futuros
`instrumentos: [EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, XAUUSD, SPX500, GER40, JPN225]`, spot/CFD. La ficha documenta que el Sharpe reportado del paper (~1.2 sobre 58 futuros diversificados) **NO es el listón**: con 9 instrumentos hay menos diversificación.

### D2 — Lookback en meses de calendario, no barras
`ret_12m` = retorno de 12 meses de calendario por instrumento, sobre su propio calendario (el motor es gap-safe). Evita el desfase "252 barras ≠ 12 meses" que el reviewer marcó.

### D3 — Sizing a 8% de vol de PORTAFOLIO (§1.2)
Pesos relativos inverso-vol con `engine.rolling_vol` (gap-safe), luego un **escalado global** para apuntar a ~8% de vol anual de portafolio (decisión del usuario, no 10% por instrumento). Acotado por `MAX_GROSS_EXPOSURE` (=4); si el escalado excede el bruto máximo, se recorta y se documenta. La ficha fija esto como la regla de `sizing`.

### D4 — Costos con swap unsigned (conservador)
La ficha anota que el motor aplica spread/slippage/swap y que el swap NO tiene dirección (siempre resta) — aproximación conservadora aceptable para trend/H001 (errar hacia abajo es seguro), pero bloqueante de H002/carry (documentado en el spec `backtest-engine`).

### D5 — Holdout EXENTO, con razón
`holdout: exento`. Razón: replicación de un paper de 1965-2009 → nuestro período (2011-2026) es OOS respecto al paper, sin tuneo. El holdout rige desde la primera hipótesis de descubrimiento (ver `hypotheses/HOLDOUT.md`, `config.HOLDOUT_START`).

### D6 — Veredicto por Sharpe neto (invariante al apalancamiento)
`metrica_exito: Sharpe neto > 0.4`. `FALSADOR: Sharpe neto < 0.2 sobre el período disponible → muerta, sin variantes`. Entre 0.2 y 0.4 = marginal. `P(pasar challenge)` del simulador queda como diagnóstico secundario, no como falsador (el óptimo de apalancamiento está diferido). La cláusula "desaparece post-2010" se subsume: nuestra muestra es casi toda post-2010.

## Risks / Trade-offs

- **La ficha promete un `sizing` que la implementación aún no tiene** → correcto para un pre-registro: es el contrato que la implementación posterior debe cumplir; si al implementar resulta inviable exactamente, se documenta la desviación en su change, no se edita el falsador.
- **Período efectivo corto para índices** (2012-2026 tras lookback) → se documenta en `universo_test`; el falsador aplica al período disponible.

## Open Questions

- Ninguna que bloquee el pre-registro. La ventana exacta por instrumento y la construcción del escalado a 8% se fijan en el change de implementación.
