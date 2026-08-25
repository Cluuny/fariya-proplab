# H008 — adquisición de datos y diagnóstico de coincidencia (Bloques 1-3)

## Por qué

La ficha de H008 está congelada. Toca medir antes de escalar, construir el perfil, y correr el
diagnóstico de COINCIDENCIA (condición 2 del falsador) que puede matar la familia por redundancia
sin construir estrategia.

## Qué cambia

- **Bloque 1 (medir antes de escalar):** descargado 1 día de aggTrades BTC+ETH. **aggTrades pesa
  poco** (BTC 1.24M filas/16MB, ETH 783k/10MB; leer 2 días 1.1s, **pico RAM 169 MB**). **(1.2)
  resuelto: aggTrades BASTA** — el perfil sale del volumen por nivel y un límite en el borde del
  VA se llena cuando un trade imprime el nivel; NO hace falta bookTicker (~10× más ligero).
  Extrapolación: 730 días × 2 ≈ **19 GB comprimido**, proceso por-día incremental → RAM no es el
  cuello (a diferencia de bookTicker).
- **Bloque 2 (datos + holdout):** muestra IN-SAMPLE sistemática (días 15/28 de cada mes 2022-09 →
  2024-02, BTC+ETH, 75 días-instrumento), checksum verificado, manifiesto versionado. Holdout
  (2024-03-01 → 2024-08-31) NO descargado; `data/raw_crypto_holdout/` creado con README de
  solo-lectura. Calidad aggTrades: 0 problemas, sin KILL. (La descarga COMPLETA de 2 años se
  difiere al Bloque 4, sólo si procede; la coincidencia no la necesita.)
- **Bloque 3 (perfil + coincidencia):** `src/crypto/volume_profile.py` (POC/VAH/VAL, bucket $10,
  área 70%), verificado a mano y con tests (POC en el bucket de mayor volumen; VA captura ≥70%;
  VA dentro del rango). **Diagnóstico de coincidencia (condición 2):** VAH≈máx 5%, VAL≈mín 4%,
  cualquiera **9% [3,16]** → la condición (2) **NO se dispara**.

## Resultado y honestidad

La coincidencia (9%) NO establece que el perfil aporte valor: el test estaba MISMATCHED — VAH/VAL
son niveles INTERIORES (el área del 70% recorta las colas), así que |VAH − máximo| grande está en
parte garantizado por definición. Es una lección sobre el diseño de la condición (2), no evidencia
fuerte del efecto. La redundancia REAL (VAH/VAL vs Bollinger; POC vs SMA/VWAP) la decide el Δ
Sharpe del Bloque 4. Registrado en el `resultado` de la ficha (sin tocar falsador/resultado_esperado).

## Impacto

- `src/crypto/volume_profile.py`, tests, `scripts/h008_coincidence.py`, manifiesto, holdout dir,
  resultado en la ficha. Zips gitignored. Suite 196 verde. PARAR en el gate de B3.3; el Bloque 4
  (estrategia) es el change SIGUIENTE, sólo porque la coincidencia < 80%. Holdout intacto.
