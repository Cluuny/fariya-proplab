# Corrección de comparabilidad del Sharpe (exceso + comisiones)

## Por qué

Antes de gastar dinero en datos de futuros, hay que asegurar que nuestro Sharpe es
comparable al de la industria (SG CTA Trend 0.14), que es el número contra el que
enmarcamos el caso de futuros. El revisor externo señaló dos problemas:

- **Problema A — Sharpe de exceso.** `engine.sharpe` no resta la tasa libre de riesgo;
  los Sharpes de la industria sí son de exceso. Premisa a verificar: ¿comparamos raw vs
  excess?
- **Problema B — comisiones.** El 0.14 de la industria es NETO de comisiones de gestión.
  Comparar nuestro bruto de backtest (sin comisión de gestión) contra un neto de la
  industria infla artificialmente el hueco de edge.

## Qué cambia

- **Problema A (verificado — NO cambia ningún número nuestro):** nuestros retornos son
  `Σ w·pct_change(precio) − costos` = ganancia de capital pura, SIN interés sobre
  colateral. En una cuenta fondeada no se cobra rf sobre el colateral, así que **nuestros
  Sharpes YA son de exceso** y directamente comparables al Sharpe de exceso de la
  industria. Restar rf sería doble-conteo (verificado numéricamente: bajaría H007-A neto
  0.184 → 0.023, un −0.162 espurio). La premisa del revisor (comparamos raw vs excess) es
  INCORRECTA para nuestro caso; su principio (usar exceso) es correcto y ya lo cumplimos.
  Se añade el parámetro `rf` a `engine.sharpe` (default 0.0, documentado) para series que
  SÍ incluyan rf, sin alterar el comportamiento por defecto.
- **Problema B (corrección real):** el 0.14 de la industria (ret 2.9% / vol 11% → rf
  implícito ≈1.4%) es neto de una comisión de gestión estándar (~2%, convención "2 y 20"
  de CTAs; rango 1.5–2.5% → Sharpe 0.28–0.37). El **bruto de comisiones ≈ 0.32**. La
  comparación correcta es **0.32 (industria, bruto de comisiones) vs 0.424 (nuestro
  requerido en futuros)** — hueco de ~30%, no de 3×. Nuestra propia H007-A (0.370) queda
  por ENCIMA del bruto de industria.
- **Veredicto:** el GO/NO-GO de futuros **NO cambia**. El criterio comprometido depende de
  dos números (bruto requerido < 0.50, N_eff > 7.5); ninguno se mueve. La corrección sólo
  reencuadra la magnitud del hueco de edge.

## Impacto

- Código: `src/engine.py` (`sharpe(rf=...)`), `tests/test_engine.py` (test de no
  doble-conteo).
- Docs: `docs/futures_case.md` y `docs/program_verdict.md` (números corregidos + nota
  explícita de veredicto sin cambio).
- Sin cambio de comportamiento por defecto (rf=0), sin delta de spec (artefacto de
  investigación/docs).
