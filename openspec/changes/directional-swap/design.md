## Context

Ver `proposal.md`. El swap unsigned dictó tres veredictos; se hace direccional y se calibra con datos reales.

## Decisions

### D1 — Dos componentes separados
`carry` (signed, la larga gana) + `swap_margin` (unidireccional). Motor:
`swap_cost = swap_margin·|w_prev| − carry·w_prev`. Es la descomposición correcta de una tabla long/short: `carry = (swap_long − swap_short)/2`, `margin = −(swap_long + swap_short)/2`.

### D2 — Carry desde tasas de política, no desde el parsing por-página
El parsing de la tabla long/short por instrumento (afterprime) dio valores inconsistentes por unidades (USDJPY≈0, imposible dado el diferencial USD-JPY). El diferencial es más fiable y consistente desde tasas de política publicadas (`(r_base − r_quote)/360`), y los cruces salen aditivos por construcción — coherente con `docs/breadth-lessons.md` (los cruces son recombinaciones). Fuente/fecha documentadas en `config`.

### D3 — Margen desde tabla de broker real
`swap_margin` desde afterprime (2026-08-23), validado contra el ejemplo de FTMO (~0.43 bp/d en EURUSD, similar). Uniforme ~0.30 bp/d (metales ~0.45). `BROKER_MARGIN_MULT` para escalar raw→prop sin número oculto.

### D4 — Renombrar swap → swap_margin
El viejo `swap` (unsigned sobre |peso|) ES el `swap_margin` (mismo comportamiento con carry=0). Los runners de hipótesis muertas se actualizan a `swap_margin=` con carry=0 → reproducen sus veredictos sin cambio.

## Risks / Trade-offs
- **Snapshot fechado**: swaps dinámicos; se documenta como SHARPE_REFERENCE. La tabla por-instrumento del broker refinaría el margen.
- **Div yields de índices aproximados**: el carry de índices usa yields típicos (documentados); es el componente más blando, pero secundario (los índices no dominan el libro).

## Open Questions
- Ninguna que bloquee. H002 (carry) ahora es implementable: es la siguiente hipótesis que aprovecha esto.
