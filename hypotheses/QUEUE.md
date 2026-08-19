# Cola de hipótesis — PropLab

Estado de las hipótesis del pipeline de investigación (Flujo 2). Las fichas
`pre_registradas` o activas viven en `hypotheses/`; las cerradas se mueven a
`hypotheses/archive/`. La fuente de verdad del veredicto de cada una es su ficha
YAML versionada.

| ID | Nombre | Familia | Estado | Nota |
|---|---|---|---|---|
| **H001** | Time-Series Momentum (TSMOM) | trend | **muerta** (falsada 2026-08-18) | Sharpe neto < 0.2 en ambas muestras sobre swap 0.3. Ficha archivada en `hypotheses/archive/H001_tsmom.yaml`; reporte en `results/H001/report.md`. |
| **H005** | Trend con vol targeting | trend | **cerrada — duplicada de H001** | Ver abajo. |
| H002 | Carry (diferencial de tasas) | carry | bloqueada (prerrequisito) | Requiere darle DIRECCIÓN al swap (diferencial con signo); con el swap unsigned actual, carry es estructuralmente incapaz de ganar. Prerrequisito en el camino crítico. |

## H005 — cerrada como duplicada de H001

H005 en la cola era "trend con vol targeting". La implementación de H001
(`src/signals.py::tsmom`) **ya usa** sizing por volatilidad inversa **y** vol
targeting de portafolio (escalado ex-ante a ~8% de vol de portafolio). Es la misma
hipótesis: el "vol targeting" no es un mecanismo de edge distinto, es la capa de
sizing que H001 ya trae. No hay una hipótesis separada que probar aquí.

**Decisión:** H005 se cierra como **duplicada de H001**. No se gasta un ciclo de
test en ella. Si en algún momento se quisiera aislar el *efecto del vol targeting*
como variable (targeting vs no-targeting), sería un estudio de sizing sobre H-x
viva, no una hipótesis de edge nueva — y hoy no hay ninguna hipótesis de trend
viva sobre la que montarlo (H001 está muerta).

## Diagnósticos de primera línea (aprendidos de H001)

Para toda hipótesis futura, antes de dar un veredicto:
- **Sharpe neto** contra el falsador pre-registrado (necesario, **no suficiente**).
- **max DD relativo a la vol**: H001 tenía −30.8% de DD con 8.8% de vol (~3.5×) —
  habría reventado una barrera del 10% aunque el Sharpe fuera 0.5.
- **turnover_anual** y **sharpe_zero_cost**: distinguen "efecto débil" de "la
  rotación se lo come". Calibración del motor (H001: ~9×/año ≈ mensual, sano).
