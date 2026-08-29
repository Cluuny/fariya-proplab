# Cola de hipótesis — PropLab · **PROGRAMA CERRADO**

> **CIERRE FORMAL (2026-08-27, change program-close-final).** Nueve familias con veredicto, CERO
> supervivientes; confirmado desde CINCO ejes independientes (suelo de costes, amplitud del terreno,
> economía del payout, volatilidad objetivo, y **convergencia del pipeline**), todos con el mismo
> veredicto: lo requerido está por encima de lo alcanzable (0.32-0.37 / N_eff 8.15). **El pipeline
> procesó 91 candidatos con 0 supervivientes → el programa se cierra por TASA (~0), no por agotar la
> cuota. Contador 91/200.** La cola está VACÍA de candidatos viables. Hallazgo positivo registrado:
> las ESTRATEGIAS sí se diversifican (ρ 0.09, N_eff 2.95) — combinar familias funciona; producir la
> primera, no. Veredicto completo en `docs/program_verdict.md`. **Reapertura sólo si se cumple una
> de las tres condiciones de `docs/reopening_conditions.md` (ninguna hoy: N_eff 8.15<14; IC 0.077<0.10;
> objetivo 0.20 no despeja), citando cuál con el número.**
>
> **Excepción registrada (2026-08-29):** H009 (AMT continuación) está PRE_REGISTRADO — la cara
> opuesta de H008 (aceptación→continuación). NO es una reapertura ni un candidato viable: es un test
> de CIERRE de la última cara abierta de la familia AMT, con datos ya descargados, sin tocar holdout,
> probabilidad previa BAJA y expectativa MUERTA/UNDERPOWERED. La cola sigue VACÍA de candidatos viables.

Estado de las hipótesis del pipeline de investigación (Flujo 2). Las fichas
`pre_registradas` o activas viven en `hypotheses/`; las cerradas se mueven a
`hypotheses/archive/`. La fuente de verdad del veredicto de cada una es su ficha
YAML versionada. **Estado final: ninguna viable.**

Numeración: se respeta el listado del documento maestro §2.5 ("las seis familias
operables"), en orden. H001 = familia 1 (trend), H002 = familia 2 (carry),
**H003 = familia 3 (estacionalidad)**, H004 = familia 4 (volatility risk premium),
H005 = familia 5 (reversión a la media a nivel índice), H006 = familia 6
(intermarket/macro).

| ID | Nombre (familia §2.5) | Familia | Estado | Nota |
|---|---|---|---|---|
| **H001** | Time-Series Momentum (TSMOM) | trend | **muerta** (falsada 2026-08-18) | Sharpe neto < 0.2 en ambas muestras sobre swap 0.3. Ficha en `hypotheses/archive/H001_tsmom.yaml`; reporte en `results/H001/report.md`. |
| **H003** | Estacionalidad — turn-of-the-month | seasonality | **muerta** (falsada in-sample 2026-08-22) | El efecto NO existe en índices 2011-2023 (concentración pooled −3.0 bps/día, IC cruza 0) y el Sharpe (0.26) está en la media del nulo (p95 0.52, p-valor 0.29). **Holdout NO tocado** (no pasó in-sample) → intacto. Ficha `hypotheses/H003_seasonality.yaml`; reporte `results/H003/report.md`. |
| **H007** | TSMOM sobre universo ampliado (17) | trend | **muerta** (falsada in-sample 2026-08-22) | Neto (swap 0.3) A=0.18/B=0.04 < 0.2 → muerta (B limpia; A sobre el placeholder de swap). Holdout intacto. **Calibración del marco: UNDERPOWERED** (diferencia H007−H001 a ~1 SE, indistinguible de ruido) → no informa la decisión de datos de futuros. `results/H007/report.md`. |
| H002 | Carry (diferencial de tasas) | carry | **RECHAZADA** (concentración) | Mejor resultado del proyecto (neto 0.282) pero muere por UMBRAL no por falsador. Motivo PRINCIPAL de rechazo: concentración short-JPY (N_eff 3.41, no es cartera es posición; carry = prima por crash → descalificante vs barrera absorbente). Coste secundario. Ver `docs/queue_triage.md`. |
| H005 | Reversión a la media (índice) | mean_reversion | **RECHAZADA-POR-COSTE** | Duty ~100%, turnover 50-100× → requerido ~0.78; bruto plausible 0.3-0.5. Cerrada sin correr. `docs/queue_triage.md`. |
| H004 | Volatility risk premium | vol_premium | fuera de alcance por datos | Necesita opciones/vol implícita; nuestro panel es OHLC spot/CFD. Requiere otra fuente de datos antes de considerarse. |
| — | **COT** (posicionamiento, no-precio) | mean_reversion | **CRIBADA-FUERA** (sin ficha) | Fuente ingerida (8 instrumentos, `data/cot_coverage.md`). Cribado condicional (`docs/cot_diagnostic.md`): Sharpe activo del fade ≈ 0 (agrupado −0.02, IC cruza 0), signo del mecanismo roto en 5/8 → no pasa el criterio (≥1.1). H008 NO se escribe. |
| H006 | Intermarket / macro | intermarket | **RECHAZADA-POR-COSTE** | Price-based, duty ~100% → requerido 0.64; sin evidencia de bruto alto (lead-lag decaído). Se cierra salvo diseño de bajo duty. `docs/queue_triage.md`. |
| **H008** | AMT / Volume Profile (cripto) | microstructure | **MUERTA** (sellada 2026-08-25, `docs/h008_block4.md`) | Novena familia. Sharpe activo del fade -0.067 ≪ listón 0.961 (con fills ≥5bps -0.986) → no viable bajo ningún supuesto. Murió por la REGLA DE SUBASTA, no por redundancia (niveles de perfil distintos de los simples, coincidencia 26%). El benchmark nulo era defectuoso (geometría rota) y su condición se retiró del veredicto. Reabierta porque el libro de cripto (bookTicker/aggTrades, gratis, ya ingerido) da volumen por nivel de precio que FX no tenía. Diseño INCREMENTAL (Δ perfil − niveles simples, bootstrap pareado) + CONDICIONAL (contexto de balance). Universo BTCUSDT+ETHUSDT (T efectiva ~189-341 con duty real 0.31). Holdout INTACTO (nunca descargado — no pasó in-sample). Ficha `hypotheses/H008_amt_volume_profile.yaml`; reporte `docs/h008_block4.md`. (Distinto del "H008" que la nota de COT dejó sin escribir.) |
| **H009** | AMT continuación (cripto) | microstructure | **PRE_REGISTRADO** (ficha 2026-08-29) | La CARA OPUESTA de H008: ACEPTACIÓN fuera del VA → continuación (momentum), no rechazo→reversión. Mecanismo económico INVERSO, no caza de variantes. **Completa la familia AMT; NO es una reapertura** (usa datos ya descargados, no toca holdout, probabilidad previa BAJA). Contexto de DESEQUILIBRIO (high−low/ATR14 > 1.5; la zona 1.0-1.5 excluida de ambas), aceptación K=3 (mismo K que el rechazo de H008), entrada límite en dirección de la extensión, geometría simétrica (objetivo/stop = 1×rango_VA). Nulo con GEOMETRÍA PRESERVADA (verificación de sanidad ~50% objetivo) — la lección de H008. Sin bruto de literatura creíble (el cribado de internet 2026-08-29 no halló validación empírica rigurosa de AMT en 40 años). Listón activo ~1.28 (duty ~0.15, menor que H008 → listón más alto); T efectiva estimada ~60-120 → RIESGO DE UNDERPOWERED declarado. Expectativa: Sharpe activo −0.3..+0.3, MUERTA o UNDERPOWERED. Ficha `hypotheses/H009_amt_continuation.yaml`. SÓLO FICHA — sin código/datos/corridas. |

## Resultado del pipeline de investigación (Flujo 2), corridas 001-003

El pipeline procesó **91 candidatos** ciegos en dos corridas (contador 91/200; la parada por
las 200 quedó SUPERADA por el cierre de amplitud). Resultado: **cero candidatos operables que
sobrevivan el cribado propio.**

- **Run 001** (`docs/pipeline_run_001.md`): 40 candidatos; el cuello no es el suministro de
  ideas sino que la mayoría de q-fin no son estrategias operables (método/teoría/modelo). Único
  operable (crypto mean reversion 15 min, arxiv:2608.21888) reporta su propio edge 1.3 bp < 5 bp
  coste — validación externa del muro del programa.
- **Run 002** (`docs/pipeline_run_002.md`): 40 candidatos; densidad por fuente Quantpedia 10% vs
  arXiv 0%. Un candidato superó el cribado de costes: **Sectoral Intramonth Momentum** (0.55) —
  pero **MUERE en el cribado aritmético** (`docs/candidate_sectoral_screen.md`: IC del Sharpe
  incluye el listón → irresoluble; deflación; TOM ≈ beta de mercado; N_eff sectores 1.29). NO
  pre-registrado.
- **Run 003:** NO ejecutada — el cribado de amplitud (`docs/terrain_breadth.md`) cerró el
  programa; correr más pipeline perdió sentido.

## Nota de numeración (histórica)

Nota sobre H005: en una revisión previa se cerró un "H005 = trend con vol
targeting" como duplicado de H001 (el vol targeting ya es la capa de sizing de
H001). Bajo la numeración del documento maestro, **H005 = reversión a la media a
nivel índice** (familia 5), hipótesis distinta que quedó **RECHAZADA-POR-COSTE**
(estado final; ya no hay cola viva). El duplicado que se cerró era el *mecanismo*
"trend+vol-targeting", no la familia 5; se conserva la nota histórica abajo.

## Nota histórica — el "trend con vol targeting" cerrado como duplicado

En una revisión previa se identificó un ítem de cola descrito como "trend con vol
targeting" y se cerró como **duplicado de H001**: el vol targeting NO es un
mecanismo de edge distinto, es la capa de sizing que H001 (`src/signals.py::tsmom`)
ya trae (vol-inversa + escalado ex-ante a ~8% de vol de portafolio). Esa decisión
sigue en pie: no se gasta un ciclo de test en "trend + vol targeting" como
hipótesis separada.

**Aclaración de numeración:** bajo el listado del documento maestro, **H005 =
reversión a la media a nivel índice** (familia 5), hipótesis DISTINTA, cerrada
como RECHAZADA-POR-COSTE (estado final; la cola ya no tiene entradas vivas). El
duplicado cerrado era el *mecanismo* trend+vol-targeting, no la familia 5. Se
conserva esta nota para no perder el rastro de la decisión.

## Diagnósticos de primera línea (aprendidos de H001)

Para toda hipótesis futura, antes de dar un veredicto:
- **Sharpe neto** contra el falsador pre-registrado (necesario, **no suficiente**).
- **max DD relativo a la vol**: H001 tenía −30.8% de DD con 8.8% de vol (~3.5×) —
  habría reventado una barrera del 10% aunque el Sharpe fuera 0.5.
- **turnover_anual** y **sharpe_zero_cost**: distinguen "efecto débil" de "la
  rotación se lo come". Calibración del motor (H001: ~9×/año ≈ mensual, sano).
