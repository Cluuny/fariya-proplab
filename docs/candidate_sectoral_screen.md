# Cribado aritmético — «Sectoral Intramonth Momentum» (candidato de la run 002)

**Fecha:** 2026-08-26. **Modo:** aritmética, SIN backtest (mismo patrón que el cribado A.4 de
H002 y el de COT: no consume intento, no requiere ficha). Fuente: `scripts/screen_sectoral.py`
sobre `src/pipeline/candidate_screen.py`. **VEREDICTO: CRIBADO_MUERE.**

El candidato (Quantpedia; Nathan/Suominen/Tasa 2026 a nivel sector) fue el PRIMERO de la
historia viva del pipeline en superar el triaje de costes (E3): Sharpe reportado **0.55**
(long-short) contra un listón de **0.44** (bruto requerido CFD al duty estimado). Antes de
pre-registrarlo, cuatro números que lo cierran gratis.

## (1.1) Deflated Sharpe — el 0.55 no sobrevive al espacio de búsqueda

SE(Sharpe) ≈ **0.192** (Lo 2002, sobre 27.5 años × 12 eventos/año). El paper describe una
estrategia de **3 patas calendáricas secuenciadas** (qué días: día 1, días 2-3, ventana 10-5
antes de fin de mes; qué dirección; qué sectores; qué orden). El espacio de búsqueda implícito
es grande. Sharpe MÁXIMO esperado por AZAR bajo N ensayos de edge cero (Bailey & López de Prado):

| N ensayos | umbral de suerte E[max] | ¿alcanza el listón 0.44? |
|---|---|---|
| 10 | 0.30 | no |
| 20 | 0.37 | no |
| 50 | 0.44 | **≈ sí** |
| 100 | 0.49 | **sí** |
| 150 | 0.51 | **sí** |
| 200 | 0.53 | **sí** |

**A N≈50-100 la SUERTE de búsqueda ya alcanza el listón 0.44.** Para una estrategia de 3 patas
calendáricas (día × dirección × sector × orden), N≥50 es plausible → el 0.55 in-sample **no
despeja deflactado**: es del orden del mejor de ~100 reglas de calendario aleatorias que
casualmente superan el suelo de costes.

## (1.2) Nulo con exposición compartida — el problema de H003

H003 (turn-of-the-month) no murió porque el TOM no exista, sino porque su Sharpe **ERA el beta
del mercado**. Una estrategia sectorial intramensual tiene el mismo riesgo: el turn-of-the-month
captura ~toda la prima de renta variable del mes. Estimación del nulo «largo del mercado en la
MISMA ventana, sectores al azar»: Sharpe de mercado ~0.45, concentrado en la ventana de mayor
deriva (×1.15) → **nulo ≈ 0.52**. El observado 0.55 **no lo supera claramente** (0.55 vs 0.52,
dentro de 1 SE). La secuencia sectorial aporta poco sobre «estar en el mercado en los días
buenos». **Es el problema de H003, otra vez.**

## (1.3) Amplitud efectiva + IC — IRRESOLUBLE

9 sectores a ρ=0.75 → amplitud efectiva **N_eff = 1.29** (casi UNA apuesta: los sectores
co-mueven). IC95 del Sharpe: **[0.17, 0.93]**. **El listón 0.44 cae DENTRO del IC.** El intervalo
no distingue 0.55 de 0.44 **ni con 27.5 años de datos** (para resolver una brecha de 0.11 al 95%
harían falta ~300+ años). **El candidato es irresoluble con los datos disponibles.**

## (1.4) Operabilidad — CORRECCIÓN honesta de la premisa

La premisa del bloque («requiere sectores US con universo point-in-time, deslistadas incluidas»)
**no aplica a esta estrategia.** Los 9 Select Sector SPDR (+ SPY) son un universo **ESTABLE**: no
se deslistan. No hay problema de survivorship/PIT a nivel ETF, y el EOD es **BARATO** (Norgate US
ETFs ~$22.50/mo, o gratis en Stooq). El PIT con deslistadas sería el problema de una estrategia de
ACCIONES individuales, no de 10 ETFs sectoriales fijos.

El bloqueante real es de **VEHÍCULO**: nuestro universo probado son 9 CFD macro (FX/índices/
materias); operar CFD de ETFs sectoriales US es una EXPANSIÓN de universo por verificar en el prop,
no un problema de datos. **Operabilidad NO es el bloqueante decisivo** — el candidato ya muere por
aritmética antes de llegar aquí.

## Veredicto

**CRIBADO_MUERE — por aritmética (1.1)+(1.2)+(1.3), no por operabilidad.**

- **(1.3) decisivo:** el IC [0.17, 0.93] incluye el listón 0.44 → 0.55 es estadísticamente
  indistinguible del suelo de costes incluso con 27.5 años (IRRESOLUBLE).
- **(1.1):** a N≥~50 la suerte de búsqueda alcanza el listón → un 0.55 in-sample de 3 patas no
  despeja deflactado.
- **(1.2):** el nulo de exposición compartida (TOM/mercado ~0.52) se come casi todo el 0.55 → la
  secuencia sectorial aporta poco (problema de H003).
- **(1.4):** operabilidad no es el bloqueante (universo ETF estable, datos baratos; sólo una
  expansión de vehículo por verificar).

**NO se pre-registra. No consume intento, no requiere ficha.** El candidato que superó el cribado
de costes muere en el cribado aritmético siguiente — exactamente el filtro barato que el programa
antepone al backtest. Confirma la lectura de la run 002: el 0.55 era un Sharpe de backtest sin
deflactar, y el cribado lo cierra sin gastar un intento.
