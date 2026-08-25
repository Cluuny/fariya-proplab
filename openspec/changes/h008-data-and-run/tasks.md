# Tareas

## Bloque 1 — medir antes de escalar
- [x] 1.1 Descargar 1 día aggTrades BTC+ETH; medir GB/tiempo/RAM (16+10MB, 1.1s, pico 169MB);
  extrapolar (730×2 ≈ 19GB, RAM no es cuello).
- [x] 1.2 Resuelto con datos: aggTrades BASTA para el mid de ejecución → NO hace falta bookTicker.
- [x] 1.3 Decisión documentada: proceso por-día incremental (pandas por día); no hace falta DuckDB.

## Bloque 2 — descarga + holdout
- [x] 2.1 Muestra in-sample (75 días-instrumento), checksum verificado, manifiesto versionado.
- [x] 2.2 Holdout físico: `data/raw_crypto_holdout/` (README solo-lectura), corte 2024-03-01;
  no descargado; el diagnóstico excluye por fecha. (Descarga completa diferida al Bloque 4.)
- [x] 2.3 Reporte de calidad aggTrades (criterio BRENT): 0 problemas, sin KILL.

## Bloque 3 — perfil + coincidencia
- [x] 3.1 `volume_profile.py` (POC/VAH/VAL, bucket $10, área 70%); verificado a mano + tests.
- [x] 3.2 Niveles simples de control (máx/mín del día = N=1) para la coincidencia.
- [x] 3.3 Diagnóstico de coincidencia: VAH≈máx 5%, VAL≈mín 4%, cualquiera 9% [3,16] → (2) NO dispara.
- [x] PARAR: reportado con caveat honesto (VAH interior → coincidencia baja parcialmente estructural).
  Bloque 4 (estrategia) = change SIGUIENTE (coincidencia < 80%). Holdout intacto.
