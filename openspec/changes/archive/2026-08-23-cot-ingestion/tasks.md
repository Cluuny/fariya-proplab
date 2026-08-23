## 1. Descarga y mapeo
- [x] 1.1 Descargar COT Legacy Futures-Only de 8 contratos (API CFTC) → data/cot/*.csv; documentar elección Legacy vs Disaggregated
- [x] 1.2 `src/cot.py` COT_CONTRACTS (con signo; falla visible si falta mapeo)
## 2. Point-in-time y calidad
- [x] 2.1 Índice por fecha de PUBLICACIÓN (martes+3); `align_to_prices` asof; test no-look-ahead
- [x] 2.2 Reporte de calidad (Brent >25% KILL); metodología documentada; los 8 PASAN
## 3. Diagnóstico y entregable
- [x] 3.1 Duty cycle disponible por instrumento (percentil rodante, p10/90 y p5/95) → gross requerido
- [x] 3.2 `data/cot_coverage.md` con cobertura, mapeo, point-in-time, calidad y duty cycle
- [x] 3.3 Tests; suite verde; commit (sin pre-registrar H008)
