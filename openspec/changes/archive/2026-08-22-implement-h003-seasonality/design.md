## Context

Ver `proposal.md`. Implementa H003 contra el contrato congelado en `hypotheses/H003_seasonality.yaml`. Reutiliza el motor (gap-safe, ex-ante) y el patrón de runner de H001.

## Decisions

### D1 — `_tom_mask(index, first_n=3, last_n=1)`
Máscara booleana sobre el índice del frame (unión de calendarios de los 3 índices; son casi el mismo calendario de equity). Un día es TOM si su rango dentro del mes (entre los días hábiles del frame) es ≤ 3 desde el inicio, o ≤ 1 desde el final. Eso da {1,2,3, último} por mes = la ventana [-1,+3] (el último de un mes es el [-1] del siguiente). ~19% de los días.

### D2 — `_long_inverse_vol(prices, active_mask, ...)` compartido con el nulo
Constructor de pesos: vol-inversa (`engine.rolling_vol`) long-only, activo sólo donde `active_mask` es True, normalizado a sum|w|=1 en días activos, con escalar ex-ante rodante (shift 1) a 8% de vol de PORTAFOLIO, recorte por max_gross. `tom_seasonal` = este constructor con la máscara TOM. El **benchmark nulo** usa el MISMO constructor con máscaras aleatorias (mismo nº de días activos por mes). Así el nulo es un control preciso: difiere sólo en QUÉ días.

### D3 — Runner: dos preguntas separadas, holdout intacto
Todo se computa sobre in-sample (2011-09-19 → 2023-08-16); el runner corta el frame ahí y NUNCA carga el holdout.
- **Existencia** (alto poder): contraste de medias del retorno diario simple en días TOM vs no-TOM, por instrumento y agrupado (pooled). IC 95% por **moving-block bootstrap** (block=20, preserva autocorrelación), 1000 resamples semilla fija. Reporta diff en bps/día + IC.
- **Explotabilidad**: Sharpe neto de `tom_seasonal` (swap 0.3 primario; 0.0/1.0 sensibilidad). **Benchmark nulo**: 1000 máscaras aleatorias (mismo nº de días/mes por mes, semilla fija) → distribución del Sharpe nulo → p95. Falsador: TOM debe superar p95.
- **Poder/CI**: IC 95% del Sharpe de TOM vía `SE ≈ √((1+S²/2)/T)`. Estado `underpowered` si el IC de TOM contiene el p95 del nulo (no se puede resolver).

### D4 — Veredicto
- TOM Sharpe claramente > p95 nulo **y** concentración con IC que excluye 0 → `viable_insample` (holdout PENDIENTE, no se toca aquí).
- TOM Sharpe claramente ≤ p95 nulo → `muerta`.
- IC de TOM cruza el p95 del nulo → `underpowered`.
El veredicto se escribe a la ficha (fecha_test, estado, resultado) sin tocar los campos congelados.

### D5 — Diagnósticos y tripwire
`turnover_anual`, `sharpe_zero_cost`, max DD/vol. **Tripwire**: si `signals.check_exposure` marca recorte por max_gross, es bug (apalancamiento esperado ~1.15×) → el runner lo reporta como alerta.

## Risks / Trade-offs
- **La expectativa es underpowered/muerta** (la propia ficha lo dice): con 12 años y SE~0.30, y un nulo con p95~0.65, es difícil que TOM lo supere de forma resoluble. Eso es un resultado legítimo, no un fallo del código.
- **Máscara sobre calendario del frame**, no per-instrumento: aceptable (índices de equity comparten calendario; long-only, días no cotizados rinden 0).

## Open Questions
- Ninguna. El holdout se aborda en un paso separado sólo si pasa in-sample.
