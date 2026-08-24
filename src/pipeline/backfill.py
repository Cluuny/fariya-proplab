"""backfill.py — cargar las 7 hipótesis existentes al esquema nuevo.

H001, H002, H003, H005, H006, H007 y COT. Es el CONJUNTO DE VALIDACIÓN del pipeline: si
el sistema no reproduce los veredictos que ya conocemos (cero supervivientes, 5/7 de clase
precio), está mal construido. Y produce el primer reporte de aprendizaje.

Los números vienen de las fichas versionadas (hypotheses/*.yaml, archive/) y de docs/
(queue_triage, cot_diagnostic, program_verdict). Notas de clasificación:
  - clase_de_dato: el proyecto trató H002/H005/H006 como la "cola price-based" (se cerró
    por coste como bloque); H003 es calendario (turn-of-the-month); COT es flujo
    (posicionamiento, no-precio). → 5/7 = precio, 1 calendario, 1 flujo.
  - fuente_de_la_idea: TODAS = 'reviewer' (las siete vinieron de una sola fuente; ése es
    justo el fallo estructural que el pipeline existe para corregir).
  - bruto_esperado = expectativa GROSS committeada antes de correr (Grinold-Kahn / ficha);
    bruto_medido = GROSS medido. SESGO A EVITAR: no se favorece a macro/flujo — la tasa de
    supervivencia por clase se MIDE, no se asume (evidencia real: 1 de 2 no-precio acertó
    algo — carry 0.28; COT dio cero exacto).
"""

from __future__ import annotations

# id, título/clasificación, registro de aprendizaje y veredicto conocido.
BACKFILL: list[dict] = [
    {
        "id": "H001",
        "titulo": "Time-Series Momentum (TSMOM), 9 instrumentos spot/CFD",
        "familia": "trend", "mecanismo": "conductual + riesgo",
        "estructura": "time_series", "direccionalidad": "long_short",
        "clase_de_dato": "precio", "fuente_de_la_idea": "reviewer",
        "fuente": "reviewer", "n_instrumentos": 9,
        "datos_requeridos": ["precio_ohlc"], "operable_en_prop": 1,
        "bruto_esperado": 0.40,   # resultado_esperado.sharpe_central (IR Grinold-Kahn)
        "bruto_medido": 0.28,     # gross ~0.244-0.308
        "duty_cycle_real": 1.0,
        "estado": "muerta", "veredicto": "falsada (neto A 0.078 / B 0.135 < 0.2)",
        "fecha_test": "2026-08-18",
    },
    {
        "id": "H002",
        "titulo": "Carry (diferencial de tasas), FX majors",
        "familia": "carry", "mecanismo": "prima por riesgo (crash)",
        "estructura": "time_series", "direccionalidad": "long_short",
        "clase_de_dato": "precio", "fuente_de_la_idea": "reviewer",
        "fuente": "reviewer", "n_instrumentos": 5,
        "datos_requeridos": ["precio_ohlc", "tasas_politica"], "operable_en_prop": 1,
        "bruto_esperado": 0.30,   # el screen esperaba que FALLARA; fue REFUTADO
        "bruto_medido": 0.495,    # gross estático; neto 0.282 (mejor del proyecto)
        "duty_cycle_real": 1.0,
        "estado": "rechazada", "veredicto": "rechazada por CONCENTRACIÓN (short-JPY, N_eff 3.41)",
        "fecha_test": None,       # cribada, no corrida formal a veredicto de Sharpe
    },
    {
        "id": "H003",
        "titulo": "Estacionalidad turn-of-the-month, índices",
        "familia": "seasonality", "mecanismo": "flujos de calendario",
        "estructura": "seasonal", "direccionalidad": "long",
        "clase_de_dato": "calendario", "fuente_de_la_idea": "reviewer",
        "fuente": "reviewer", "n_instrumentos": 3,
        "datos_requeridos": ["precio_ohlc", "calendario"], "operable_en_prop": 1,
        "bruto_esperado": 0.35,   # sharpe_absoluto_central (casi todo beta); exceso esperado ~0
        "bruto_medido": 0.26,     # Sharpe absoluto medido = media del nulo
        "duty_cycle_real": 0.19,  # ventana [-1,+3] ≈ 4 de ~21 días
        "estado": "muerta", "veredicto": "falsada (exceso sobre nulo ≈ 0, IC cruza 0)",
        "fecha_test": "2026-08-22",
    },
    {
        "id": "H005",
        "titulo": "Reversión a la media a nivel índice",
        "familia": "mean_reversion", "mecanismo": "sobrerreacción",
        "estructura": "time_series", "direccionalidad": "long_short",
        "clase_de_dato": "precio", "fuente_de_la_idea": "reviewer",
        "fuente": "reviewer", "n_instrumentos": 4,
        "datos_requeridos": ["precio_ohlc"], "operable_en_prop": 1,
        "bruto_esperado": 0.40,   # plausible 0.3-0.5; requerido ~0.78
        "bruto_medido": None,     # cerrada por coste SIN correr
        "duty_cycle_real": None,
        "estado": "rechazada_coste", "veredicto": "rechazada-por-coste (turnover 50-100× → req ~0.78)",
        "fecha_test": None,
    },
    {
        "id": "H006",
        "titulo": "Intermarket / macro (lead-lag)",
        "familia": "intermarket", "mecanismo": "difusión de información",
        "estructura": "time_series", "direccionalidad": "long_short",
        "clase_de_dato": "precio", "fuente_de_la_idea": "reviewer",
        "fuente": "reviewer", "n_instrumentos": 6,
        "datos_requeridos": ["precio_ohlc"], "operable_en_prop": 1,
        "bruto_esperado": None,   # sin evidencia de bruto alto (lead-lag decaído)
        "bruto_medido": None,     # cerrada por coste SIN correr
        "duty_cycle_real": None,
        "estado": "rechazada_coste", "veredicto": "rechazada-por-coste (duty ~100% → req 0.64)",
        "fecha_test": None,
    },
    {
        "id": "H007",
        "titulo": "TSMOM sobre universo ampliado (17 instrumentos)",
        "familia": "trend", "mecanismo": "conductual + riesgo",
        "estructura": "time_series", "direccionalidad": "long_short",
        "clase_de_dato": "precio", "fuente_de_la_idea": "reviewer",
        "fuente": "reviewer", "n_instrumentos": 17,
        "datos_requeridos": ["precio_ohlc"], "operable_en_prop": 1,
        "bruto_esperado": 0.33,   # rango ficha [0.29, 0.37]
        "bruto_medido": 0.370,    # muestra A (primaria); B 0.229
        "duty_cycle_real": 1.0,
        "estado": "muerta", "veredicto": "falsada (neto A 0.184 / B 0.040); marco UNDERPOWERED",
        "fecha_test": "2026-08-22",
    },
    {
        "id": "COT",
        "titulo": "COT — fade de posicionamiento (no-precio)",
        "familia": "mean_reversion", "mecanismo": "reversión de posicionamiento",
        "estructura": "time_series", "direccionalidad": "long_short",
        "clase_de_dato": "flujo", "fuente_de_la_idea": "reviewer",
        "fuente": "reviewer", "n_instrumentos": 8,
        "datos_requeridos": ["precio_ohlc", "cot_posicionamiento"], "operable_en_prop": 1,
        "bruto_esperado": 0.20,   # criterio de cribado <0.7 (activo); se esperaba señal débil
        "bruto_medido": 0.0,      # Sharpe activo del fade ≈ 0 (agrupado −0.02, IC cruza 0)
        "duty_cycle_real": None,  # diagnóstico por episodios, no un backtest de serie
        "estado": "cribada_fuera", "veredicto": "cribada-fuera (activo ≈ 0; signo roto en 5/8)",
        "fecha_test": None,
    },
    # --- microestructura: entran al registro para COMPETIR, con su rechazo motivado ---
    {
        "id": "MP001",
        "titulo": "Auction Market Theory / Volume Profile (VAH/VAL/POC)",
        "familia": "microstructure", "mecanismo": "subasta / value area",
        "estructura": "time_series", "direccionalidad": "long_short",
        "clase_de_dato": "flujo", "fuente_de_la_idea": "humano",
        "fuente": "manual", "n_instrumentos": 4,
        "frecuencia": "intraday_bar",
        "requiere_volumen_consolidado": 1, "requiere_cinta_tick": 0, "requiere_order_book_l2": 0,
        "costo_datos_usd_mes": 133.0,   # IQFeed core $108.15 + futuros $24.87 (dtn, 2025-12)
        "datos_requeridos": ["barras_1min", "volumen_consolidado"], "operable_en_prop": 0,
        "requiere_test_incremental": 1,
        "estado": "rechazada_por_datos",
        "veredicto": (
            "rechazada por DATOS: volume profile intradía necesita barras 1-min + volumen "
            "consolidado (IQFeed ~$133/mo) > presupuesto $60/mo; Norgate (EOD, ~$22.50/mo) NO "
            "lo habilita. Además requeriría test INCREMENTAL vs niveles simples (máx/mín N días)."),
        "bruto_esperado": None, "bruto_medido": None, "duty_cycle_real": None, "fecha_test": None,
    },
    {
        "id": "ICT001",
        "titulo": "ICT / Smart Money Concepts (order blocks, fair value gaps)",
        "familia": "microstructure", "mecanismo": "'liquidez institucional' (no verificable)",
        "estructura": "time_series", "direccionalidad": "long_short",
        "clase_de_dato": "flujo", "fuente_de_la_idea": "humano",
        "fuente": "manual", "n_instrumentos": 1,
        "frecuencia": "intraday_bar",
        "requiere_volumen_consolidado": 0, "requiere_cinta_tick": 0, "requiere_order_book_l2": 0,
        "costo_datos_usd_mes": 0.0,     # se define sobre el gráfico → NO necesita dato externo (ése es el fallo)
        "datos_requeridos": ["precio_ohlc"], "operable_en_prop": 0,
        "estado": "rechazada_por_falsabilidad",
        "veredicto": (
            "rechazada por FALSABILIDAD (filtro #1): order blocks / fair value gaps se "
            "identifican dibujándolos sobre el gráfico después, no consultando dónde había "
            "órdenes. No hay dato externo que los confirme o refute. Distinción de CATEGORÍA, "
            "no de estilo ni prejuicio."),
        "bruto_esperado": None, "bruto_medido": None, "duty_cycle_real": None, "fecha_test": None,
    },
]


def load_backfill(conn) -> int:
    """Upsert the known hypotheses (7 EOD + 2 microestructura). Returns count. Idempotent.

    Las 7 originales son EOD y coste de datos 0 (default aplicado aquí); las 2 de
    microestructura declaran su frecuencia y coste explícitamente.
    """
    from src.pipeline import db

    db.init_db(conn)
    for rec in BACKFILL:
        rec = {"frecuencia": "EOD", "costo_datos_usd_mes": 0.0, **rec}  # default EOD/gratis
        db.upsert(conn, rec)
    return len(BACKFILL)
