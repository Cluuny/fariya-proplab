# Tareas

- [x] 0 Bloqueante de disco (19 GB vs 7.3 GB libres) detectado y decidido: procesar TODOS los días
  incrementalmente, DESCARTAR el raw (pico ~1 día), retener resúmenes por-día. `h008_build_summary.py`
  (concurrente, resumable). El backtest del Bloque 4 hará igual.
- [x] 1 Muestra completa procesada: 1094 días-instrumento (547 BTC + 547 ETH, 2022-09-01→2024-02-29).
  Holdout (2024-03→08) NO descargado.
- [x] 2 T efectiva recalculada con la muestra real: balance-regime 60%, edge-touch → 642 episodios
  (duty 59% cota superior), T efectiva ~356-642 ≥ 150. NO underpowered (matiz: selectividad real = rechazo, medido en B4).
- [x] 3 Reporte de calidad muestra completa: 0 precios cero/neg, 0 tamaños neg, 0 días faltantes, sin KILL.
- [x] 4 Bollinger bien emparejado (banda de vol de 1 DÍA, no 20): VAH≈banda_sup 8%, VAL≈banda_inf 5%,
  POC≈VWAP 18%, cualquiera 26% [23,28] → (2) NO dispara sobre la muestra completa.
- [x] 5 ResearchGate añadido a la estación 1 (ingesta manual, mismos filtros) + test.
- [x] 6 NO se corre el Bloque 4; T ≥ 150 reportada. Holdout intacto.
