# Tareas

- [x] 1 Filtro de rechazo medido (klines 1m, incremental/ligero): de 643 edge-touch, 341
  sobreviven (mid re-entra al VA en ≤3 barras) → duty 31%, supervivencia 53%.
- [x] 2 Listón recalculado sobre duty real: Sharpe activo requerido 0.961 (a priori 1.139),
  rt/día 0.31, requerido bruto cripto 0.476; T efectiva ~189-341.
- [x] 3 T efectiva ≥ 150 → no hace falta decisión de ampliar/parar; poder suficiente.
- [x] 4 Desviación del pre-registro registrada en la ficha (duty 0.20→0.31, listón recalc),
  sin tocar falsador/resultado_esperado.
- [x] 5 Expectativa refutada registrada: coincidencia 26% (no >60-80%), niveles NO redundantes;
  matiz distintos≠mejores (Δ Sharpe del B4 decide).
- [x] 6 NO se corre el Bloque 4; listón sobre duty real reportado. Holdout intacto.
