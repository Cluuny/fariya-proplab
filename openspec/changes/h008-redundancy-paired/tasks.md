# Tareas

- [x] 1 Klines 1d (BTC/ETH, 2022-08→2024-02) descargados, movidos al store inmutable y
  manifestados (SHA256) — para SMA(20)/Bollinger(20). aggTrades ya estaban.
- [x] 2 Diagnóstico INTERIOR vs INTERIOR (`scripts/h008_redundancy_paired.py`): VAH-Boll_sup,
  VAL-Boll_inf, POC-SMA20, POC-VWAP24h; cada uno % + IC95.
- [x] 3 DISTRIBUCIÓN de distancias (mediana + p25/p75/p90), no sólo el % bajo umbral.
- [x] 4 Atención POC vs VWAP: 28% [18,38], mediana 36 bps → POC NO es un VWAP caro.
- [x] 5 Criterio: condición (2) del falsador congelado, tolerancia 10 bps y umbral 80% IDÉNTICOS.
  Resultado: cualquiera 32% ≪ 80% → (2) NO dispara.
- [x] 6 Registrado en la ficha como corrección de DISEÑO DEL TEST (sustituye el mal emparejado);
  falsador/resultado_esperado intactos.
- [x] 7 Coincidencia < 80% → adelante el Bloque 4 (change siguiente). Holdout intacto.
