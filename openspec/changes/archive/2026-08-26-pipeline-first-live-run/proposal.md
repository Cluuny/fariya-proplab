# Primera corrida real del pipeline — extracción en sesión

## Why

El pipeline está construido y validado contra el backfill (11 veredictos
reproducidos), pero NUNCA ha procesado un paper que no conocíamos. Esta es la
primera corrida sobre papers ciegos. Responde la pregunta de fondo del programa:
¿el cuello de botella es el SUMINISTRO de ideas o el ACCESO a datos/vehículo? El
embudo por estación (D1) lo mide directamente.

Modo de ejecución: las estaciones 4 (extracción) y 5 (adversario) las corre Claude
Code EN SESIÓN, sin API externa — mismo patrón que la validación de `extract`
(`docs/extraction_validation.md`), que ya funcionó. Consecuencia aceptada y
registrada: el pipeline NO es automatizable en este modo (cada corrida requiere
sesión interactiva); viable para 40 candidatos, tedioso para 200. La API
(`make_api_extractor`) se cablea SÓLO si esta corrida produce candidatos útiles;
el seam queda documentado y sin conectar.

## What Changes

**Eficiencia — el orden importa.** Las estaciones 1-3 son DETERMINISTAS y se corren
PRIMERO en batch (no consumen sesión). Solo lo que sobrevive a E3 llega a sesión.

1. **Estimador determinista del abstract** (`src/pipeline/estimate.py`, NUEVO). Hoy
   E3 (costes) NO puede correr sobre candidatos de arXiv porque nadie llena
   `frecuencia`/`duty_cycle_estimado`/`bruto_reportado` desde el abstract (el runner
   los deja en None y salta el triaje). Se convierte esa parte a HEURÍSTICA
   determinista: reglas de palabras clave (frecuencia, duty, clase de dato,
   turnover) + extracción por regex del Sharpe reportado si está EN EL ABSTRACT
   (con `cita_bruto = "abstract"`; ausente → null → `requiere_lectura`). Sin modelo.
2. **Fix de red** (`discover.py`): `ARXIV_API` de `http://` → `https://` (el http
   devuelve 301 y rompe E1).
3. **Prioridad determinista** (`estimate.priority_score`): score para ordenar el
   procesamiento en sesión por prioridad descendente (si hay que cortar por tiempo,
   se cortan los peores). Wire en `cmd_triage`: E2 keep → estimar → E3 → score.
4. **Corrida** (`scripts/pipeline_run_001.py`): E1 (arXiv q-fin PM/ST/TR + barrido
   microestructura + RSS Alpha Architect/CXO), PARAR en 40 candidatos procesados por
   E1-E3 (no consumir la cuota de parada de 200). E4-E5 en sesión SOLO sobre
   supervivientes de E3, por prioridad descendente.
5. **Eje nuevo del adversario ya presente** (`nulo_preserva_geometria`, del change
   anterior) se aplica en E5.
6. **Entregable** `docs/pipeline_run_001.md` (autosuficiente): D1 embudo por estación,
   D2 tasa de rechazo por tipo de fuente, D3 fichas de los 3-5 que llegan a la
   compuerta (con cita de ubicación del bruto y findings del adversario incl.
   `hallazgo_no_enumerado`), D4 `hallazgo_no_enumerado` (todos), D5 los muertos en E3
   con el número, D6 contador de parada X/200, D7 coste de sesión (papers, tokens,
   cuántos caben por sesión → si 200 es alcanzable o hace falta la API).
7. **Lectura humana comprometida**: los que lleguen a la compuerta se leen íntegros
   por el operador aunque el adversario diga KEEP. MÉTRICA: problemas reales que el
   operador encontró y el adversario NO — es la medida del alcance del adversario, y
   esta corrida ciega ES el test ciego que no se pudo montar aparte.

**NO se pre-registra ninguna hipótesis en esta corrida. Solo se producen candidatos.**

## Impact

- NUEVO: `src/pipeline/estimate.py` + tests; `scripts/pipeline_run_001.py`.
- MOD: `src/pipeline/discover.py` (https), `scripts/pipeline.py` (`cmd_triage` llama al estimador).
- NUEVO doc: `docs/pipeline_run_001.md`. Actualiza `docs/extraction_defects.md` (métrica adversario-vs-operador) y `docs/research_pipeline.md` (nota: no automatizable en modo sesión).
- DB `data/pipeline/research.db`: +≤40 filas procesadas (counter 11 → ≤51 / 200).
- Reglas anti-alucinación (cita-o-null, figura→null, sin-falsador→rechazo) obligatorias en E4.
- Sin API cableada. Holdout intacto. Sin pre-registro.
