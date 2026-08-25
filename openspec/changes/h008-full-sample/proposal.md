# H008 — muestra completa antes del Bloque 4

## Por qué

La muestra in-sample eran 75 días-instrumento (días 15/28 de cada mes) → **≈15 episodios** →
las condiciones (1) y (3) del falsador saldrían UNDERPOWERED POR CONSTRUCCIÓN (SE(Ŝ)≈0.27,
IC95≈±0.53), el mismo defecto que se corrigió en el falsador v2. Además los días 15/28 caen
sistemáticamente cerca de vencimientos y del turn-of-the-month → no es muestreo aleatorio.

## Qué cambia

- **Bloqueante de disco detectado y decidido:** la muestra completa (~19 GB comprimido) NO cabe
  (7.3 GB libres). DECISIÓN (ficha 1.3): procesar TODOS los días del in-sample
  (2022-09-01 → 2024-02-29, BTC+ETH) **incrementalmente, descartando el raw** (pico de disco
  ~1 día), reteniendo resúmenes por-día. `scripts/h008_build_summary.py`, resumable. El backtest
  del Bloque 4 se hará igual (descargar→simular→descartar). Holdout (2024-03→08) NO se descarga.
- **(2) T efectiva recalculada con datos reales** (klines 1d del in-sample completo): balance-
  regime = **60%** de los días (656/1094); con edge-touch conditional ~0.55 → ~361 episodios raw,
  **T efectiva ~200-361 según simultaneidad BTC/ETH → ≥ 150.** El in-sample completo NO es
  underpowered por construcción (la muestra 15/28 sí lo era). El edge-touch real se mide al
  procesar la muestra.
- **(3) Reporte de calidad** sobre la muestra completa (por-día en el resumen: precios cero,
  tamaños negativos; días faltantes).
- **(4) Bollinger bien emparejado:** banda de vol recomputada sobre ventana de **1 DÍA** (la del
  perfil), no 20 → `scripts/h008_redundancy_1day.py` (VAH vs banda_sup(1d), VAL vs banda_inf(1d),
  POC vs VWAP) sobre la muestra completa. La comparación 20-día vs 1-día no decía nada.
- **(5) ResearchGate** añadido como fuente de la estación 1 (ingesta manual, mismos filtros).

## Impacto

- Scripts (summarizer incremental, redundancia 1-día), discover.py (+ResearchGate), ficha
  (`resultado.muestra_completa`), tests. Raw NO retenido (disco); resúmenes por-día en results
  (gitignored). Suite verde. **NO se corre el Bloque 4** hasta tener la muestra procesada y la T
  reportada (T ≥ 150 confirmada). Holdout intacto. Sin delta de spec.
