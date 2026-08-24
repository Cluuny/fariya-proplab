"""pipeline — el esqueleto del pipeline de investigación (Flujo 2).

Estaciones 1-3 de la cadena de descubrimiento de hipótesis, más el esquema de
ficha estructurado (SQLite, NO un RAG) y el registro de aprendizaje. El orden de
las estaciones corrige el diseño de junio: el filtro que más mata es la ARITMÉTICA
DE COSTOS (H005/H006 murieron sin correrse), así que va ANTES de leer el paper.

  1. Descubrimiento         (discover.py)     — arXiv API + RSS, cron MENSUAL
  2. Triaje de operabilidad (triage_operability.py)
  3. Triaje de costos       (triage_costs.py) — el filtro nuevo, barato y discriminante

Fuera de alcance por ahora (sólo si el mes de futuros da luz verde): extracción con
LLM, revisión adversaria, generación de stubs (estaciones 4-7).
"""
