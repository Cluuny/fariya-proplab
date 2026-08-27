# Cribado de amplitud del terreno — ¿hay N_eff suficiente en algún universo accesible?

**Fecha:** 2026-08-26. **Modo:** aritmética sobre datos que YA existen (fapi Binance gratis,
parquet CFD local, proxies ETF de Yahoo gratis). Fuente: `scripts/terrain_breadth.py`.
**N_eff = (Σλ)²/Σλ²** sobre los autovalores de la matriz de correlación de retornos diarios
(participation ratio; mismo que `scripts/effective_breadth.py`).

**VEREDICTO: NO para todos. Ningún universo accesible tiene la amplitud para que su techo de IR
supere el listón. Es el cierre del programa por AMPLITUD.**

## Contexto — por qué esta es la pregunta que decide

Nueve familias murieron; al menos cuatro por AMPLITUD, no por falta de señal: H002 (N_eff FX
3.41, casi todo short-JPY), H007 (N_eff 5.32 tras DUPLICAR instrumentos a 17), el candidato
sectorial (N_eff 1.29 con 9 sectores), H008 (2 instrumentos a ρ 0.8). El patrón se repetía. La
pregunta directa: **¿cuál es el N_eff MÁXIMO alcanzable con universos que podemos operar Y pagar
($125/mes)?** Y su techo de IR (≈ IC·√N_eff), ¿supera algún listón medido?

## La tabla

| universo | N_eff | $/mes | IR techo (IC .02) | IR techo (IC .05) | ¿supera 0.64/0.65/0.96? |
|---|---|---|---|---|---|
| CFD Dukascopy 17 | **5.02** | ~0 | 0.045 | 0.112 | **NO** |
| **Cripto perps 30 (Binance)** | **2.16** | **0** | 0.029 | 0.073 | **NO** |
| Futuros CME ~26 (proxy ETF) | 8.15 | ~50 | 0.057 | 0.143 | NO |
| ETFs sector/país/factor ~25 | 3.31 | 0 | 0.036 | 0.091 | NO |
| Cripto + CFD (combinado) | 4.36 | ~0 | 0.042 | 0.104 | NO |
| Futuros + Cripto (combinado) | 5.83 | ~50 | 0.048 | 0.121 | NO |

Listones medidos: **CFD 0.64 · cripto perp 0.65 · activo a duty 31% 0.96** (`docs/cost_floor.md`,
`program_verdict.md`). Techo del bloque: IR ≈ IC·√N_eff.

- **CFD 17:** N_eff 5.02 (2022 días; 5.32 en la ventana larga de `effective_breadth.py`). Techo
  IC.05 = 0.11 → **6× por debajo** de 0.64.
- **Cripto perps 30 — la medición más importante (acceso ilimitado, gratis):** N_eff = **2.16**,
  correlación mediana **0.68**. **Todo correlaciona con BTC; la cola de altcoins NO añade
  dimensiones.** Treinta instrumentos genuinos de cripto valen ~2 apuestas independientes. Techo
  IC.05 = 0.073 → **9× por debajo** de 0.65. (Nota honesta: el «top 30 por volumen» de Binance hoy
  incluye perps TOKENIZADOS de TradFi — XAU, NVDA, MSTR, SOXL — que inflarían el N_eff porque son
  exposición de acciones/oro reempaquetada, NO amplitud de cripto; se excluyeron. Con ellos el
  N_eff sube artificialmente, pero esa dimensión ya la da el universo CFD/futuros, no es nueva.)
- **Futuros CME ~26 (el mejor, proxy ETF, requiere Norgate ~$50/mes):** N_eff 8.15, correlación
  mediana 0.10. Es el universo más ANCHO accesible. Techo IC.05 = 0.143 → **4.5× por debajo** de
  0.64.
- **ETFs sector/país/factor (gratis):** N_eff 3.31 — **replica, no añade**: los sectores y países
  co-mueven (corr mediana 0.49); no aporta dimensiones sobre lo que los índices macro ya dan.
- **Combinaciones:** cripto + CFD = 4.36, futuros + cripto = 5.83 — **combinar NO rescata**: cripto
  aporta poco (N_eff 2 y algo correlacionado con el riesgo global), y la ventana común se encoge.

## Robustez a la frecuencia de rebalanceo (el caveat honesto)

El techo IC·√N_eff asume UNA apuesta independiente por activo al año. Un rebalanceo mensual da
BR = 12·N_eff (×√12 = 3.46 sobre el techo anual). Aun así:

| universo | IR mensual (IC .05) | IR mensual (IC .02) | vs 0.64 |
|---|---|---|---|
| Futuros 26 (el mejor) | **0.49** | 0.20 | **NO** |
| CFD 17 | 0.39 | 0.16 | NO |
| Cripto 30 | 0.26 | 0.10 | NO (vs 0.65) |

**Para superar 0.64 con IC.05 mensual haría falta N_eff ≥ 14. Ningún universo accesible llega**
(el máximo, futuros proxy, es 8.15). Sólo se despeja bajo supuestos que el programa NO tiene:
(a) un IC ELITE ≥ 0.10 — el programa nunca produjo señal cerca de eso (OFI ~0, H008 negativo,
carry el mejor a 0.495 bruto y ya limitado por amplitud); o (b) rebalanceo semanal+ a IC alto —
donde el IC empírico CAE (los signos de momentum/carry apenas cambian semana a semana → las
apuestas no son independientes) y, si de verdad rotaras rápido, el SUELO DE COSTES INTRADÍA
(el muro original del programa) vuelve a cerrar. **Las dos paredes se cierran juntas: a baja
frecuencia falta amplitud; a alta frecuencia sobra coste. No hay frecuencia intermedia en la que
un universo accesible despeje.**

## Conclusión — el cierre definitivo del programa

**NO existe un universo accesible ($125/mes) cuyo techo de IR supere el listón de 0.64.** El
número duro: el máximo alcanzable es ~**0.14** (futuros, IC 0.05, techo del bloque) o **0.49**
(futuros, IC 0.05, mensual) — contra un listón de **0.64** (y **0.96** ajustado por duty). El
universo con acceso ILIMITADO y gratis (cripto) es el PEOR: **N_eff 2.16**, un terreno de ~2
apuestas independientes.

Esto es más fundamental que el suelo de costes. Aunque tuvieras una señal perfecta al máximo del
rango plausible (IC 0.05) y datos gratis ilimitados, **la amplitud efectiva del terreno accesible
es demasiado pequeña para generar un information ratio que despeje el objetivo comprometido de
0.40 neto.** El cuello no es la señal ni el coste por separado: es que el terreno no tiene
suficientes apuestas independientes.

**Es más informativo decir esto que correr cuatro corridas más del pipeline.** Por eso, y siguiendo
la regla del propio bloque («si B cierra el programa, la run 003 pierde sentido»), la run 003 NO se
ejecuta. El pipeline funciona y está limpio; el terreno es el que no da.

**Caveats registrados (para no sobre-afirmar):** el cierre es relativo (a) al objetivo comprometido
de 0.40 neto — con la mitad de ambición (0.20 neto → listón ~0.44) el futuros mensual a IC.05
(0.49) rozaría, pero 0.40 es el objetivo del programa; y (b) a los IC que el programa ha
DEMOSTRADO (bajos) — un IC elite cambiaría el cálculo, pero no hay evidencia de tenerlo. Bajo el
objetivo y la señal reales, ningún terreno accesible despeja.
