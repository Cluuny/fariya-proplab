# Tareas

- [x] 1 Estrategia pre-registrada implementada (contexto+trigger+entrada límite+salidas, maker/
  funding) — `src/crypto/h008_backtest.py` + tests.
- [x] 2 Dos ramas PAREADAS (perfil vs simple banda-1día/VWAP), MISMOS episodios; Δ Sharpe por
  bootstrap pareado por episodio. Integridad del pareado reportada (268/341 compartidos).
- [x] 3 Benchmark nulo (niveles al azar, 1000×, semilla 20260824), p95 del Sharpe activo.
- [x] 4 Veredicto por las tres condiciones separadas + underpowered disponible en (1b).
- [x] 5 Holdout NO tocado (no pasó in-sample).
- [x] D1-D9 en `docs/h008_block4.md` (veredicto, pareado, ramas, nulo, fills+sensibilidad,
  salidas, poder, expectativa, cómputo). Autosuficiente para el reviewer.
- [x] Registrado en la ficha (resultado.bloque4, estado no_promociona, fecha_test) sin tocar
  falsador/resultado_esperado. QUEUE.md actualizado. Suite 203 verde.
