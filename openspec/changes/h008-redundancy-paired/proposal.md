# H008 — coincidencia BIEN EMPAREJADA antes del Bloque 4

## Por qué

El diagnóstico de coincidencia (condición 2 del falsador) se corrió con emparejamiento
INCORRECTO: VAH (nivel INTERIOR, el área del 70% recorta las colas por construcción) contra el
máximo del día (EXTREMO). El 9% estaba garantizado por geometría, no por información. Hay que
correrlo bien emparejado ANTES del Bloque 4. Es aritmética pura sobre datos ya descargados.

## Qué cambia

- `scripts/h008_redundancy_paired.py`: INTERIOR contra INTERIOR (misma tolerancia 10 bps, mismo
  umbral 80% — corrección de DISEÑO DEL TEST, no de criterio):
  - |VAH − Bollinger_sup(20,2σ)|, |VAL − Bollinger_inf(20,2σ)|, |POC − SMA(20)|, |POC − VWAP(24h)|.
  - Reporta cada uno con % + IC95 **y la DISTRIBUCIÓN de distancias** (mediana + p25/p75/p90).
- Datos: klines 1d (BTC/ETH, 2022-08 → 2024-02) descargados, movidos al store inmutable
  (`data/raw_crypto/.../monthly/klines/`) y manifestados (SHA256). aggTrades ya estaban.

## Resultado (75 días-instrumento in-sample)

| comparación | % ≤10bps | IC95 | mediana |
|---|---|---|---|
| VAH ≈ Bollinger_sup | 4% | [0,8] | 415 bps |
| VAL ≈ Bollinger_inf | 0% | [0,0] | 666 bps |
| POC ≈ SMA(20) | 0% | [0,0] | 283 bps |
| **POC ≈ VWAP(24h)** | **28%** | [18,38] | **36 bps** |
| cualquiera | 32% | [21,43] | — |

**Condición (2) NO dispara (32% ≪ 80%).** El emparejamiento MÁS limpio (POC vs VWAP, mismo
timescale y tipo) da 28% con mediana 36 bps: **el POC NO es un VWAP caro** — el modo del volumen
difiere de la media ~36 bps. Bollinger/SMA(20) son bandas MULTI-DÍA vs perfil de 1 día → otro
desajuste de timescale, se ponderan menos. La REDUNDANCIA de niveles NO queda establecida → la
pregunta incremental sigue ABIERTA, la decide el Δ Sharpe del Bloque 4.

Registrado en el `resultado` de la ficha (sustituye el test mal emparejado; falsador y
resultado_esperado intactos).

## Impacto

- Script, klines manifestados, resultado en la ficha, reporte. Suite 196 verde. Zips gitignored.
  Coincidencia < 80% → **adelante el Bloque 4** (estrategia). Holdout intacto. Sin delta de spec.
