# Tareas

## 3.1 Comisión maker/taker
- [x] 3.1a Comisión VIP0 verificada (maker 0.02%, taker 0.05%; binance.com, 2026-08-24).
- [x] 3.1b `fraccion_maker` parametrizada; `comision_round_trip`.

## 3.2 Funding EVITABLE
- [x] 3.2a Cortes fijos 00/08/16 UTC verificados; ~0.01%/período por defecto.
- [x] 3.2b Modelado como función de cruces con posición abierta (cruces=0 → 0), NO continuo.
- [x] 3.2c Registrado: primera estructura de costes que PREMIA estar fuera del mercado.

## 3.3 Slippage del libro
- [x] 3.3 Estimado del spread medido de datos reales (~0.03 bp), no asumido; nota sobre
  órdenes que barren el libro.

## Entregable + comparación
- [x] E1 Tabla `sharpe_bruto_requerido` cruzada por round-trips × maker × funding (vol real ~60%).
- [x] E2 Coste por unidad de riesgo reproduce el pivote (taker 0.032, maker 0.013 < MES 0.063).
- [x] E3 Comparación honesta vs CFD 0.64 / MES 0.85 (favorable por unidad de riesgo; iguala
  en nivel sólo en maker+baja frecuencia+sin funding), con caveat de convención.
- [x] E4 CLI `scripts/crypto_costs.py`, tests verdes, sección en `docs/cost_floor.md`.
