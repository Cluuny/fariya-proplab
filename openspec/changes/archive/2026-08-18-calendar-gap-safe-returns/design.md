## Context

Ver `proposal.md`. Reproducido en `engine._asset_returns`: con un hueco de calendario, `pct_change().fillna(0)` pone en 0 el día del hueco Y el de reapertura → el retorno cruzado se pierde. El guard de look-ahead sintético no lo veía (calendarios alineados). Además, hallazgos de higiene: el `source` del anclaje no citaba procedencia, y la política de holdout (§3.5) no estaba escrita.

## Goals / Non-Goals

**Goals:** retornos seguros ante huecos; guard sobre calendarios desalineados; procedencia del anclaje; política de holdout explícita con la exención de H001.

**Non-Goals:** darle dirección al swap (H002); implementar H001; conseguir un tick independiente exacto del S&P (se documenta la limitación).

## Decisions

### D1 — `ffill` del precio por columna antes de `pct_change`
`engine._asset_returns` hace `prices.ffill().pct_change()`. Efecto por columna: día no cotizado → precio del cierre previo → retorno 0; día de reapertura → precio real → retorno cruzado correcto, atribuido a la reapertura. NaN iniciales (antes de que exista el instrumento) no se rellenan (no hay dato previo) → 0, y ahí no hay posición. **Alternativa:** dropear NaN y reindexar por instrumento — más complejo y propenso a desalineación; `ffill` es local y correcto.

### D2 — Guard sobre calendarios desalineados
`_misaligned_prices` construye dos instrumentos donde uno tiene ~15% de días faltantes. Los tests cheat/honest corren sobre eso, y un test extra verifica el cruce de hueco (día del hueco=0, reapertura=retorno real). **Por qué:** el riesgo real es el desajuste de 3 calendarios (SPX500 vs FX), invisible con un `bdate_range` alineado.

### D3 — Procedencia del anclaje (honestidad)
El `source` de `SHARPE_REFERENCE` cita Wikipedia "Closing milestones of the S&P 500" (índice ~1200 mid-sep 2011, <1100 para 2011-10-04; consultado 2026-08-18) como corroboración del nivel, y anota que un cierre diario independiente exacto no se logró en sesión (Stooq CSV vacío, FRED 10y). Un anclaje sin procedencia es una afirmación; se documenta lo verificado y lo pendiente.

### D4 — Política de holdout con exención explícita de H001
`hypotheses/HOLDOUT.md` + `config.HOLDOUT_START = 2023-08-17`. H001 exenta (replicación externa de MOP-2012, período OOS respecto al paper, sin tuneo). El holdout rige desde la primera hipótesis de descubrimiento/optimización. Cada ficha declara si aplica; por omisión, aplica. **Por qué escribirlo:** el reviewer y §3.5 exigen que sea una decisión explícita, no una omisión.

## Risks / Trade-offs

- **`ffill` podría enmascarar un instrumento delistado/con hueco largo** (mantiene el último precio indefinidamente) → para huecos normales de calendario es correcto; un hueco anómalo largo ya lo marca `loaders` (calendar_gap/missing_days). No se rellena leading NaN.
- **El anclaje sigue sin un tick independiente exacto** → mitigado citando la corroboración y documentando el pendiente; el hito 2 se mantiene verde por la ventana emparejada y la corroboración de rango.

## Open Questions

- Registrar un cierre diario independiente del S&P (Stooq/Yahoo ^SPX 2011-09-19) con su fecha de consulta para cerrar del todo la verificación externa: pendiente, no bloqueante.
