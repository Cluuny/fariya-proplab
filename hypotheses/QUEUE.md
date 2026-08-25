# Cola de hipótesis — PropLab

Estado de las hipótesis del pipeline de investigación (Flujo 2). Las fichas
`pre_registradas` o activas viven en `hypotheses/`; las cerradas se mueven a
`hypotheses/archive/`. La fuente de verdad del veredicto de cada una es su ficha
YAML versionada.

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
| **H008** | AMT / Volume Profile (cripto) | microstructure | **PRE_REGISTRADO** (2026-08-24) | Novena familia, FUERA de la condición de parada. Reabierta porque el libro de cripto (bookTicker/aggTrades, gratis, ya ingerido) da volumen por nivel de precio que FX no tenía. Diseño INCREMENTAL (Δ perfil − niveles simples, bootstrap pareado) + CONDICIONAL (contexto de balance, duty 20% → Sharpe activo requerido ~1.14). Benchmark nulo con exposición compartida. Sin literatura arbitrada; probabilidad previa BAJA (listón >2× el mejor del proyecto). Universo BTCUSDT+ETHUSDT (T efectiva ~162 tras ρ≈0.8); holdout corte 2024-03-01. Ficha `hypotheses/H008_amt_volume_profile.yaml`. SOLO ficha — sin código ni datos. (Distinto del "H008" que la nota de COT dejó sin escribir.) |

Nota sobre H005: en una revisión previa se cerró un "H005 = trend con vol
targeting" como duplicado de H001 (el vol targeting ya es la capa de sizing de
H001). Bajo la numeración del documento maestro, **H005 = reversión a la media a
nivel índice** (familia 5), que es una hipótesis distinta y sigue viva en cola.
El duplicado que se cerró era el *mecanismo* "trend+vol-targeting", no la familia
5; se conserva la nota histórica abajo para no perder el rastro.

## Nota histórica — el "trend con vol targeting" cerrado como duplicado

En una revisión previa se identificó un ítem de cola descrito como "trend con vol
targeting" y se cerró como **duplicado de H001**: el vol targeting NO es un
mecanismo de edge distinto, es la capa de sizing que H001 (`src/signals.py::tsmom`)
ya trae (vol-inversa + escalado ex-ante a ~8% de vol de portafolio). Esa decisión
sigue en pie: no se gasta un ciclo de test en "trend + vol targeting" como
hipótesis separada.

**Aclaración de numeración:** bajo el listado del documento maestro, **H005 =
reversión a la media a nivel índice** (familia 5), que es una hipótesis DISTINTA y
sigue viva en cola. El duplicado cerrado era el *mecanismo* trend+vol-targeting,
no la familia 5. Se conserva esta nota para no perder el rastro de la decisión.

## Diagnósticos de primera línea (aprendidos de H001)

Para toda hipótesis futura, antes de dar un veredicto:
- **Sharpe neto** contra el falsador pre-registrado (necesario, **no suficiente**).
- **max DD relativo a la vol**: H001 tenía −30.8% de DD con 8.8% de vol (~3.5×) —
  habría reventado una barrera del 10% aunque el Sharpe fuera 0.5.
- **turnover_anual** y **sharpe_zero_cost**: distinguen "efecto débil" de "la
  rotación se lo come". Calibración del motor (H001: ~9×/año ≈ mensual, sano).
