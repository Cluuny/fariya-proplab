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
| **H007** | TSMOM sobre universo ampliado (17) | trend | **muerta** (falsada in-sample 2026-08-22) | Neto (swap 0.3) A=0.18/B=0.04 < 0.2 → muerta. Holdout intacto. **Calibración del marco:** dirección correcta (amplitud→más bruto) pero magnitud NO fiable (la predicción de ficha estaba mal derivada por desajuste de período). Ficha/reporte: `hypotheses/H007_tsmom_expanded.yaml`, `results/H007/report.md`. |
| H002 | Carry (diferencial de tasas) | carry | bloqueada (prerrequisito) | Requiere darle DIRECCIÓN al swap (diferencial con signo); con el swap unsigned actual, carry es estructuralmente incapaz de ganar. Prerrequisito en el camino crítico. |
| H004 | Volatility risk premium | vol_premium | fuera de alcance por datos | Necesita opciones/vol implícita; nuestro panel es OHLC spot/CFD. Requiere otra fuente de datos antes de considerarse. |
| H006 | Intermarket / macro | intermarket | en cola | Lead-lag entre mercados; cuidar el filtro 4 (¿por qué existe el edge?). |

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
