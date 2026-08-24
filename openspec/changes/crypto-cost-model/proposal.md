# Pivote a cripto — Bloque 3: modelo de costes cripto

## Por qué

El suelo de costes es un régimen distinto en cripto: 24/7 (365 días/año), comisión
maker/taker, y funding EVITABLE. Sin este modelo no se puede cribar ninguna hipótesis de
cripto por coste (el filtro que más mata en el proyecto). Precios y estructura verificados
de fuentes públicas.

## Qué cambia

- **`src/crypto/cost_model.py`**, tres componentes:
  - **(3.1) Comisión maker/taker** VIP0 VERIFICADA (maker 0.02%, taker 0.05%;
    binance.com/en/fee/futureFee, 2026-08-24). `fraccion_maker` parametriza el suelo —
    proveer liquidez paga <½ que cruzar el spread.
  - **(3.2) Funding EVITABLE**: cortes fijos 00/08/16 UTC, ~0.01%/período; modelado como
    función de los cruces de corte con posición abierta, NO como cargo continuo. Cruces=0
    → coste 0. Primera estructura de costes del proyecto que PREMIA estar fuera del mercado.
  - **(3.3) Slippage** estimado del propio libro: spread medido de datos reales (BTCUSDT
    2024-01-02) ~0.03 bp → despreciable para tamaño de mejor nivel; órdenes que barren el
    libro añaden slippage a medir.
- **Entregable**: tabla `sharpe_bruto_requerido` cripto cruzada por round-trips (1,2,5,10)
  × fracción maker (0/50/100%) × funding en corte (sí/no). Sobre la vol REAL medida (~60%).
- **Comparación honesta** contra CFD swing 0.64 y MES intradía 0.85: por unidad de riesgo
  cripto (maker 0.013 / taker 0.032) queda por DEBAJO de MES 0.063 (favorable, reproduce el
  pivote); en nivel absoluto sólo iguala a 0.64/0.85 en la esquina maker + baja frecuencia +
  funding evitado (maker 1 rt/día = 0.65). Caveat de convención documentado.
- CLI `scripts/crypto_costs.py`, tests, sección en `docs/cost_floor.md`.

## Impacto

- `src/crypto/cost_model.py`, script, tests, doc. Precios/vol/spread verificados o medidos
  de datos reales. Sin nuevas deps. Sin delta de spec. Infra/cribado.
