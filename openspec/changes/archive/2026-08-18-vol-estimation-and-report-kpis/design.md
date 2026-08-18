## Context

Ver `proposal.md`. Medido en datos reales sobre el DataFrame combinado (unión de 9 instrumentos): la vol ingenua de SPX500 (con ceros de `ffill`) es 13.3% vs 16.9% sobre días propios → **21% de deflación** (JPN225 similar; EURUSD ~2%). El `source` del anclaje mezclaba lo externo con lo interno. El reporte arrastró copy 3 veces.

## Goals / Non-Goals

**Goals:** vol por días propios (`rolling_vol`); nombrar la verificación del anclaje; documentar `ffill` en colas; KPIs del reporte generados del repo.

**Non-Goals:** implementar el sizing de H001 (usará `rolling_vol`); verificar los endpoints del S&P contra una fuente inalcanzable en sesión; regenerar el HTML completo del reporte por comando (por ahora sólo los KPIs).

## Decisions

### D1 — `engine.rolling_vol` estima sobre días propios
Por columna: `prices[col].dropna().pct_change().rolling(window).std() × √(bars_por_año propios)`, reindexado (ffill) al frame. Descarta los huecos (no los ceros de relleno) → la vol del índice no se deflacta. **Alternativa:** enmascarar los ceros en la serie ffilled — equivalente pero más frágil; `dropna` por instrumento es directo y es lo que pidió el review.

### D2 — Nombrar la verificación del anclaje
El `source` distingue: EXTERNO = la serie es el índice (endpoints coinciden con cierres públicos); si es el índice, su Sharpe es el del índice por construcción — no es comparación contra un paper. INTERNO = 0.80 (geométrico) vs 0.82 (aritmético), acuerdo entre estimadores. Pendientes anotados: endpoint final y tick independiente exacto (no alcanzables en sesión). **Por qué:** que el yo futuro no crea que comparó contra Moskowitz-Ooi-Pedersen.

### D3 — `ffill` en colas
`ffill` extendería el último precio si una serie termina antes. Hoy no aplica; se documenta en el spec como limitación conocida para cuando se añada un instrumento de historia más corta.

### D4 — `scripts/report_kpis.py`
Computa desde el repo: tests (pytest --collect-only), PRs mergeados (gh), instrumentos activos (config), specs/changes (ls), holdout, Sharpe de referencia. El reporte toma sus KPIs de aquí. **Por qué:** el reporte es el único artefacto a mano → deriva; la regla del README exige regenerable con un comando. No se genera el HTML completo aún (narrativa), sólo los KPIs, que es donde estaba el arrastre.

## Risks / Trade-offs

- **`rolling_vol` reindex+ffill del estimador** en días de hueco → el sizing usa el último estimado; correcto (la vol no cambió en un día no cotizado). Alternativa (NaN en huecos) complicaría el sizing.
- **`report_kpis.py` depende de `gh`/red para PRs** → si no hay red, el conteo de PRs sale 0; el resto (tests, config, ls) es local. Aceptable; el KPI de PRs es el menos crítico.

## Open Questions

- Ventana por defecto de `rolling_vol` (63 días ≈ 3 meses): default razonable para H001; se fija en la ficha de H001.
- Generar el HTML completo del reporte por comando (no sólo KPIs): mejora futura; fuera de alcance.
