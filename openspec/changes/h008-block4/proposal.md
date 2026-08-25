# H008 Bloque 4 — estrategia condicional, Δ Sharpe y benchmark nulo

## Por qué

La ficha está congelada (falsador y resultado_esperado intactos). Listón vigente: Sharpe ACTIVO
requerido 0.961 (duty real 0.31). Toca ejecutar el Bloque 4 y producir el reporte autosuficiente
para el reviewer.

## Qué cambia

- **`src/crypto/h008_backtest.py`** (+tests): simulador de la estrategia pre-registrada (contexto
  balance, extensión+rechazo, entrada límite en el borde, salida objetivo/stop/time-stop) con
  comisión maker/taker, funding si cruza un corte, y supuesto de fills parametrizable.
- **`scripts/h008_block4.py`**: dos ramas PAREADAS (perfil VAH/VAL→POC vs simple banda-1día→VWAP),
  MISMOS episodios (definidos por el contexto), Δ Sharpe por bootstrap pareado; benchmark nulo
  (niveles al azar, 1000×, semilla 20260824); sensibilidad de fills (≥5 bps). Genera
  `docs/h008_block4.md` (D1-D9, autosuficiente).
- Datos ya locales (klines 1m/1d manifestados + perfiles del resumen); NO se re-descargó aggTrades.

## Resultado (in-sample 2022-09→2024-02, holdout INTACTO)

**VEREDICTO: NO PROMUEVE.** Sharpe activo de la rama perfil **−0.067** (341 episodios) ≪ listón
0.961 → NO viable. Falsador por condición: (1) Δ Sharpe (perfil−simple) −0.966 IC95 [−2.54,+0.53]
CRUZA 0 → UNDERPOWERED en la dimensión incremental (no muerta por 1); (2) coincidencia 26% → no
dispara; (3) activo −0.067 > p95 del nulo −2.041 → no dispara (SUPERA al nulo, p≈0.000).

Hallazgo honesto: los niveles de perfil SÍ llevan información vs fading aleatorio (el nulo pierde
~−3.4; el perfil queda en ~0), pero el edge es ~0 tras costes — DISTINTOS e informativos, NO
rentables. El fade de extensiones en un mercado momentum-driven no genera dinero. Sensibilidad de
fills: con cruce ≥5 bps el activo cae a −0.986; el veredicto NO cambia. ADVERTENCIA registrada: el
modelo de fills nunca se construyó; el resultado lleva el supuesto de fill-al-toque encima.

Registrado en la ficha (`resultado.bloque4`, estado no_promociona, fecha_test 2026-08-24), sin
tocar falsador/resultado_esperado. Expectativa comprometida CUMPLIDA en dirección (no promueve).

## Impacto

- Backtest + tests (203 verde), reporte D1-D9, ficha, QUEUE.md. **Holdout INTACTO** (no pasó
  in-sample, no se descarga). Sin delta de spec. El operador envía `docs/h008_block4.md` tal cual.
