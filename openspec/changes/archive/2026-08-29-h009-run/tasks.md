# Tasks — h009-run

## 1. Implementación y corrida
- [x] 1.1 `scripts/h009_run.py`: embudo de episodios por contexto (desequilibrio >1.5, extensión, aceptación K=3), reutilizando `src/crypto/h008_backtest.py`.
- [x] 1.2 D1 — PARADA OBLIGATORIA: duty real, rt/día, episodios crudos, T efectiva por coincidencia REAL BTC/ETH (no la cota cruda), listón recalculado. Verificar T efectiva ≥ 60 antes de seguir.
- [x] 1.3 Backtest incremental: ramas perfil vs simple, episodios por CONTEXTO, Δ Sharpe pareado (bootstrap), compartidos reportados.
- [x] 1.4 Nulo geometría preservada (semilla 20260829, 1000 resamples) con verificación de sanidad ~50% ANTES del veredicto.
- [x] 1.5 Veredicto con las tres condiciones independientes del falsador.

## 2. Entregables
- [x] 2.1 `docs/h009_run.md` auto-suficiente D1–D9 (incluye mecanismo honesto del 9% del nulo).
- [x] 2.2 Ficha `hypotheses/H009_amt_continuation.yaml`: gestión de cola + bloque resultado. NO tocar FALSADOR ni resultado_esperado.
- [x] 2.3 `hypotheses/QUEUE.md`: fila H009 + nota de excepción → veredicto.

## 3. Verificación
- [x] 3.1 Suite verde (255 passed, 1 skipped).
- [x] 3.2 Holdout NO tocado (2024-03→08 nunca descargado; in-sample corta en 2024-02-29).
