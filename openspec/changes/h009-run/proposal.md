# H009 — implementación y corrida (AMT continuación)

## Why

H009 (la cara de CONTINUACIÓN de AMT: aceptación fuera del área de valor → momentum, el mecanismo
económico INVERSO de H008 que era fade→reversión) quedó PRE_REGISTRADA con su ficha congelada en el
change anterior. Este change la IMPLEMENTA y la CORRE contra su falsador, sin tocar el FALSADOR ni el
`resultado_esperado` (congelados) y sin tocar el holdout (2024-03→08, nunca descargado). Es un test de
CIERRE de la última cara abierta de la familia AMT, no una reapertura del programa (probabilidad previa
BAJA, datos ya descargados).

## What Changes

- **`scripts/h009_run.py`** (nuevo): orquesta la corrida completa reutilizando `src/crypto/h008_backtest.py`.
  - **PARADA OBLIGATORIA D1**: mide duty real, round-trips/día, episodios crudos y **T efectiva** ANTES
    del backtest. T efectiva por coincidencia REAL BTC/ETH (37 solo + 1.11×32 pares a ρ0.8 = 73), no la
    cota cruda-conservadora (56, que asume todo coincidente y disparaba una PARADA falsa). Regla del
    bloque: si T efectiva < 60, PARAR y reportar. Medido 73 ≥ 60 → procede. Listón recalculado sobre el
    duty real: 0.40/√0.092 + 0.245 = 1.560.
  - **Backtest incremental**: dos ramas pareadas (perfil VAH/VAL vs banda simple 1-día), episodios por
    CONTEXTO (desequilibrio + extensión + aceptación K=3), Δ Sharpe con bootstrap pareado sobre los
    compartidos.
  - **Nulo con geometría preservada** (entrada aleatoria en el rango del día, objetivo/stop ±1×rango_VA
    simétrico, semilla 20260829, 1000 resamples) con **verificación de sanidad ANTES del veredicto**.
  - **Veredicto** con las tres condiciones independientes del falsador.
- **`docs/h009_run.md`** (nuevo): reporte auto-suficiente D1–D9.
- **`hypotheses/H009_amt_continuation.yaml`**: gestión de cola (estado→muerta, intentos→1, fecha_test) +
  bloque `resultado`. NO se toca FALSADOR ni resultado_esperado.
- **`hypotheses/QUEUE.md`**: fila H009 y nota de excepción → veredicto.

## Resultado

**MUERTA / NO VIABLE** por el falsador (condición 3): Sharpe activo perfil **−1.190** ≪ listón **1.560**.
El Δ perfil−simple (+4.325, IC no cruza 0) confirma que los niveles de perfil NO son redundantes con la
banda simple, pero la REGLA de subasta no genera edge. El nulo marcó geometría ROTA (objetivo 9%, no
~50%) por objetivo LEJANO (±1×rango_VA), NO el defecto de H008 (objetivo detrás) → condición (2) no usada
por conservadurismo; el veredicto no depende de ella. Expectativa: dirección CUMPLIDA (muerta), magnitud
REFUTADA (−1.190 fuera de −0.3..+0.3, peor de lo esperado). La familia AMT queda COMPLETA: ambas caras
negativas (fade H008 −0.067, continuación H009 −1.190). El veredicto del programa (nueve familias, cero
supervivientes) no cambia. Holdout INTACTO.

## Impact

- Specs: ninguno (`skip_specs: true` — artefacto de investigación, no cambia comportamiento del sistema).
- Código: `scripts/h009_run.py` nuevo; reutiliza `src/crypto/h008_backtest.py` sin modificarlo.
- Suite: 255 passed, 1 skipped (verde).
- Holdout: NO tocado.
