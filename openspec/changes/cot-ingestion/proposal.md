## Why

Todo lo probado hasta ahora es precio puro → competimos contra todos los que tienen precios. COT es la primera fuente NO-de-precio: posicionamiento (comerciales cubren, especuladores toman el otro lado, el desequilibrio extremo revierte — filtro 4 limpio). Y su perfil de coste es de DUTY CYCLE BAJO por diseño (solo se opera en extremos) → gross requerido ~0.42-0.47 en vez de 0.64, el único camino que puede pasar el filtro #6 tras el triaje del Bloque 1.

## What Changes

- **`src/cot.py`** (nuevo): mapeo instrumento↔contrato CFTC (con signo; USDJPY/USDCAD invierten; falla visible si falta), carga POINT-IN-TIME (índice = fecha de publicación = martes + 3 días), `net_spec` (neto de specs, normalizado por OI), `align_to_prices` (asof, cada día ve el último reporte YA PUBLICADO).
- **`data/cot/*.csv`** (8 instrumentos, descargados de la API CFTC Legacy Futures-Only, 2026-08-23).
- **`scripts/cot_diagnostic.py`** + **`data/cot_coverage.md`** (entregable): cobertura (criterio Brent), mapeo, alineación point-in-time, calidad, y duty cycle disponible por instrumento.
- **`tests/test_cot.py`** (+3): mapeo falla visible, índice por publicación, y NO-look-ahead point-in-time (un reporte del martes no aparece hasta el viernes).

## Resultado

- Formato **Legacy** (specs vs commercials, historia más larga; Disaggregated cambió metodología en 2009).
- **8 de 17** tienen COT (EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, XAUUSD, XAGUSD, SPX500); los cruces/índices no-US no.
- **Los 8 PASAN** (0-0.1% faltante era 2000+; metales desde 1986). Posicionamiento MUY persistente (AC 0.85-0.98 → extremos en episodios de semanas).
- **Duty cycle disponible ~20-30% (p10/90) o ~11-18% (p5/95) → gross requerido ~0.45** (vs 0.64 always-in). Baja el listón ~0.20 de Sharpe.

NO se pre-registra H008: la ficha se escribe con estos números a la vista.

## Capabilities

### New/Modified Capabilities
<!-- Fuente de datos nueva (COT) + módulo. La garantía point-in-time la fija test_cot. skip_specs=true. -->

## Impact

- **Código**: `src/cot.py`, `scripts/cot_diagnostic.py`, `tests/test_cot.py`. **Datos**: `data/cot/*.csv` (referencia, committeados), `data/cot_coverage.md` (entregable).
- Primera fuente no-de-precio; habilita una hipótesis (H008) con gross requerido ~0.45.
