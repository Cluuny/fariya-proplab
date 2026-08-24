"""crypto — pivote a cripto: datos e infraestructura (NO se asume que hay edge).

Cripto se adopta porque el TERRENO es investigable a coste cero: datos de libro de
órdenes gratuitos e ilimitados (mejor calidad que todo lo usado hasta ahora), estructura
de costes por unidad de riesgo favorable, y la posibilidad de operar con capital propio
sin barrera absorbente. La conclusión del ciclo CFD (`docs/program_verdict.md`) sigue
vigente y no se revisa. Ver `docs/crypto_pivot.md`.

Tres bloques de INFRAESTRUCTURA Y CRIBADO (no consumen intentos, no tocan holdout, no
requieren ficha):
  1. Ingesta y persistencia   (ingest.py, quality.py)
  2. Validación del OFI        (ofi.py, calibrate.py) — Cont, Kukanov & Stoikov 2011
  3. Modelo de costes cripto   (cost_model.py)
"""
