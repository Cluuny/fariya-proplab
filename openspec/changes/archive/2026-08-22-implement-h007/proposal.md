## Why

La ficha de H007 está revisada y corregida (holdout respetado, N_eff explícito). Toca implementar y correr **in-sample** (→ 2023-08-16, holdout intacto). La señal `tsmom` NO se modifica. El punto real de la corrida es la **calibración del marco** (¿acertó la predicción de bruto?), no el veredicto de la hipótesis (se esperaba muerta).

## What Changes

- **`scripts/run_h007.py`** (nuevo): reusa `signals.tsmom` sin cambios sobre el universo de 17; dos muestras (A: FX+metales 2005→2023-08-16 con 2008; B: los 17, 2015→2023-08-16). Reporta **BRUTO y NETO por separado** (la trampa: calibración sobre bruto, falsador sobre neto). Incluye baseline **period-matched** (H001 recomputado al mismo corte) para una calibración sin el confound de período.
- **Veredicto** escrito a `hypotheses/H007_tsmom_expanded.yaml` (estado, resultado, veredicto) sin tocar campos congelados; reporte `results/H007/report.md`.

## Resultado

- **Falsador (neto 0.3):** A=0.184, B=0.040 → ambos < 0.2 → **muerta** (esperado). El swap unsigned hunde el bruto, igual que H001.
- **Calibración (bruto):** medido A=0.370, B=0.229. Contra la predicción de ficha [0.29,0.37] → mixto. **Hallazgo:** la predicción estaba MAL DERIVADA (usó H001-a-2026, B=0.308; el B period-matched a 2023-08-16 es 0.030 — el trend moderno del universo-9 estaba ~muerto). Corregido el período, la ampliación ayudó MÁS de lo predicho (B 0.030→0.229). **Veredicto de marco: dirección correcta, magnitud no fiable** → tratar el caso de datos de futuros como dirección, no estimación puntual.

## Capabilities

### New/Modified Capabilities
<!-- Ninguna: runner + veredicto (reusa la señal `tsmom` existente). skip_specs=true. -->

## Impact

- **Código**: `scripts/run_h007.py` (nuevo). Sin cambios en `signals`/`engine`.
- **Artefactos**: veredicto en la ficha, `results/H007/report.md`, `QUEUE.md`. Holdout NO tocado.
- Tercer trend falsado; la lección es de MARCO (la predicción puntual falló por período, la dirección se sostuvo).
