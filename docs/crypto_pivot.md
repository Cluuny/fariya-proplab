# Pivote a cripto — por qué se cambia de vehículo (con los números)

Se cierra el ciclo CFD/futuros como vehículo principal. **La conclusión del ciclo CFD
(`docs/program_verdict.md`) sigue vigente y NO se revisa:** cero supervivientes, método
correcto, restricciones de datos y vehículo. Cripto se adopta no porque se haya
establecido que hay edge —**NO se ha establecido**— sino porque el TERRENO es investigable
a coste cero y la estructura de costes por unidad de riesgo es favorable.

## Las tres razones, con números

1. **Datos de libro de órdenes gratuitos e ilimitados** — mejor calidad que todo lo usado
   hasta ahora. `data.binance.vision` publica volcados históricos SIN cuenta ni API key. Un
   día de `bookTicker` de BTCUSDT perpetuo son **~199 MB / 18.5M filas** con mejor bid/ask
   **y tamaños** — exactamente el dato Level-I que necesita el OFI (imposible de conseguir
   gratis en FX/CFD). Verificado 2026-08-24: bookTicker, aggTrades y bookDepth PRESENTES
   (aunque el README de binance/binance-public-data no liste bookTicker, existe).

2. **Coste por unidad de riesgo favorable** (~**0.033** vs ~**0.063** de MES). La vol de BTC
   es ~3× la del MES mientras que las comisiones son sólo ~1.6× → coste/riesgo ≈ 1.6/3 ≈
   0.53×. Verificable: taker round-trip 0.10% / vol diaria ~3% = **0.033** (coincide). Con
   órdenes límite (maker 0.04% round-trip) baja a ~0.013. Detalle en el modelo de costes
   cripto (Bloque 3).

3. **Operar con capital propio sin barrera absorbente** — se elimina la barrera de challenge
   de las prop firms (el falsador que descalificó a H002 por concentración/crash era, en el
   fondo, sobre la barrera absorbente). No se contrata ninguna prop firm.

## Lo que este pivote NO afirma

- **NO** se ha establecido que exista edge en cripto. Sólo que hay terreno investigable y
  gratis, y que la estructura de costes es favorable.
- Estos tres bloques son **INFRAESTRUCTURA Y CRIBADO**: no consumen intentos, no tocan el
  holdout, no requieren ficha. Ninguna hipótesis se pre-registra todavía.
- El ciclo CFD no se reabre ni se contradice.

## Los tres bloques

1. **Ingesta y persistencia** (`src/crypto/ingest.py`, `quality.py`; change
   crypto-data-ingestion). Volcados a `data/raw_crypto/` INMUTABLE, manifiesto SHA256
   versionado, verificación contra el checksum de Binance, reporte de calidad con el mismo
   criterio que mató a BRENT (KILL si falta >25% de un período). Universo inicial: **sólo
   BTCUSDT perpetuo**; ventana inicial 5 días, midiendo GB/tiempo antes de escalar.
2. **Validar el OFI** (`ofi.py`, `calibrate.py`; change ofi-validation). Fórmula exacta de
   Cont, Kukanov & Stoikov (2011, arXiv 1011.6402) §2.1. Criterio de aceptación: R² medio
   >0.40 en regresión contemporánea por media hora, y OFI mejor que trade imbalance.
3. **Modelo de costes cripto** (`cost_model.py`; change crypto-cost-model). Comisión
   maker/taker, funding EVITABLE (premia estar fuera del mercado), slippage del propio libro.

## Lo que NO se hace todavía

- NO se mide la curva de decaimiento predictivo (siguiente change, sólo si el Bloque 2 valida).
- NO se pre-registra ninguna hipótesis.
- NO se construye modelo de fills (va después; prerrequisito de cualquier hipótesis de order flow).
- NO se contrata ninguna prop firm.
