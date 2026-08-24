"""extraction_validation.py — corre las fichas EXTRAÍDAS EN SESIÓN (validación manual asistida)
por las estaciones 4 (validate_extraction) y 5 (adversarial.evaluate) reales.

Las fichas de abajo son la SALIDA del extractor (el LLM = esta sesión) leyendo los PDFs de
data/papers/, con cita de ubicación por cada numérico. El objetivo es comprobar que la lógica
ya construida acepta/rechaza como debe, y que el adversario detecta los defectos clave
(MOP degradación post-2010; OFI R² contemporáneo, no predictivo; TOM = beta de mercado).
"""

from __future__ import annotations

from src.pipeline import adversarial, extract

# ---- fichas EXTRAÍDAS del PDF (con cita_<campo> por cada numérico) ----
EXTRACTED = {
    "moskowitz2012_tsmom": {
        "titulo": "Time Series Momentum",
        "familia": "trend", "mecanismo": "subreacción conductual + prima de transferencia de riesgo",
        "hipotesis": "el signo del retorno de exceso a 12 meses predice positivamente el retorno del mes siguiente",
        "regla_entrada": "long si ret_exceso_12m > 0, short si < 0; holding 1 mes (k=12, h=1)",
        "regla_salida": "rebalanceo mensual",
        "n_instrumentos": 58, "cita_n_instrumentos": "Abstract; §1 ('58 in total')",
        "bruto_reportado": None,  # el Sharpe del factor diversificado está en Figure 2 (gráfico), no en texto extraíble
        "cita_bruto": None,       # → por regla (a) va null; NO se inventa 1.2
        "requiere_lectura_manual": 1,  # regla (c): el ~1.2 está SÓLO en Figure 2 → lectura manual
        "nota_figura": "Sharpe ~1.2 del factor diversificado en Figure 2 (Panel A)",
        "periodo_original": "1985-2009 (primario; 'report results post-1985')",
        "cita_periodo": "§2.3 p.15; §4.1 p.16 ('sample period 1985 to 2009')",
        "falsador": "si el Sharpe NETO (tras costes) < 0.2 en nuestro universo/período, se descarta y no se reintenta con variantes",
        "clase_de_dato": "precio",
    },
    "mcconnell2008_tom": {
        "titulo": "Equity Returns at the Turn of the Month",
        "familia": "seasonality", "mecanismo": "flujos de calendario (fin/inicio de mes)",
        "hipotesis": "el exceso de retorno del mercado se concentra en la ventana de 4 días del cambio de mes",
        "regla_entrada": "long el mercado en la ventana [-1,+3] del cambio de mes, flat el resto",
        "regla_salida": "salir al 3er día hábil del mes",
        "n_instrumentos": None,  # CRSP: mercado US completo (VW/EW) → universo enorme
        "cita_n_instrumentos": "p.1 ('CRSP daily returns', VW/EW market)",
        "bruto_reportado": None, "cita_bruto": None,   # dan retornos medios diarios, no un Sharpe
        "periodo_original": "1987-2005 primario (19 años); 1926-2005 (80 años CRSP)",
        "cita_periodo": "Abstract; p.1-2",
        "falsador": "si el exceso de la ventana TOM sobre el nulo (4 días aleatorios) no es positivo ni significativo, se descarta",
        "clase_de_dato": "calendario",
    },
    "hurst2017_trend": {   # sustituto del test ciego (NO es hipótesis del proyecto)
        "titulo": "A Century of Evidence on Trend-Following Investing",
        "familia": "trend", "mecanismo": "time series momentum a través de clases y del tiempo",
        "hipotesis": "el trend-following da retornos positivos cada década desde 1880",
        "regla_entrada": "combinación de trend a 1/3/12 meses, long/short",
        "regla_salida": "rebalanceo periódico",
        "n_instrumentos": None, "cita_n_instrumentos": None,   # en el cuerpo/tablas, no leído
        "bruto_reportado": None, "cita_bruto": None,           # Sharpe en tablas/figuras
        "requiere_lectura_manual": 1,
        "periodo_original": "1880-2016 (un siglo, datos reconstruidos)",
        "cita_periodo": "Abstract ('since 1880')",
        "falsador": "si el Sharpe neto < 0.2 en nuestro universo/período, se descarta",
        "clase_de_dato": "precio",
    },
    "contkukanov2011_ofi": {
        "titulo": "The Price Impact of Order Book Events",
        "familia": "microstructure", "mecanismo": "impacto lineal del desbalance de flujo (OFI) en el mid",
        "hipotesis": "el OFI explica el cambio de precio CONTEMPORÁNEO de forma lineal (ΔP_k = β·OFI_k)",
        "regla_entrada": "(no hay regla operativa en el paper; es un modelo de impacto contemporáneo)",
        "regla_salida": "n/a",
        "n_instrumentos": 50, "cita_n_instrumentos": "§3.1 ('50 U.S. stocks')",
        "bruto_reportado": 0.65, "cita_bruto": "§3.2 / Abstract ('average R² of 65%') — es R², no Sharpe",
        "periodo_original": "abril 2010",
        "cita_periodo": "§3.1 ('one calendar month (April, 2010)')",
        "falsador": "si el R² contemporáneo < 0.40 o si el OFI no PREDICE el retorno futuro tras costes, se descarta",
        "clase_de_dato": "flujo",
    },
}

# ---- hallazgos del REVISOR ADVERSARIO (True = la ficha SUPERA el ataque en ese eje) ----
# Los dos últimos ejes (autores_independientes, literatura_previa_posterior) se AÑADIERON tras
# el test ciego: el adversario NO los detectó espontáneamente (ver docs/extraction_defects.md).
ADVERSARIAL = {
    "moskowitz2012_tsmom": {
        "periodo_descubrimiento": True, "n_variantes": True, "sesgo_supervivencia": True,
        "datos_no_rt": True, "costes_plausibles": True,
        "degradacion_post_pub": False,    # degradación documentada post-2010 (CXO) → FLAG
        "contemporaneo_vs_predictivo": True, "benchmark_cero": True,
        "autores_independientes": True,   # es el hallazgo ORIGINAL, no se presenta como replicación
        "literatura_previa_posterior": True,
    },
    "mcconnell2008_tom": {
        "periodo_descubrimiento": True, "n_variantes": True, "sesgo_supervivencia": True,
        "datos_no_rt": True, "costes_plausibles": True, "degradacion_post_pub": False,
        "contemporaneo_vs_predictivo": True,
        "benchmark_cero": False,          # CRÍTICO: long-only en la ventana = beta de mercado
        "autores_independientes": True, "literatura_previa_posterior": True,
    },
    "contkukanov2011_ofi": {
        "periodo_descubrimiento": True, "n_variantes": True, "sesgo_supervivencia": True,
        "datos_no_rt": True, "costes_plausibles": True, "degradacion_post_pub": True,
        "contemporaneo_vs_predictivo": False,  # CRÍTICO: R² CONTEMPORÁNEO, no predictivo
        "benchmark_cero": True,
        "autores_independientes": True, "literatura_previa_posterior": True,
    },
    "hurst2017_trend": {   # con los ejes NUEVOS ya explícitos, el conflicto autoral SÍ se marca
        "periodo_descubrimiento": True, "n_variantes": True,
        "sesgo_supervivencia": False,     # backtest a un siglo sobre datos reconstruidos (décadas tempranas)
        "datos_no_rt": True, "costes_plausibles": True,
        "degradacion_post_pub": False,    # trend degradó post-2010
        "contemporaneo_vs_predictivo": True, "benchmark_cero": True,
        "autores_independientes": False,  # Ooi y Pedersen = 2/3 de MOP → NO es confirmación independiente
        "literatura_previa_posterior": True,
    },
}


def main():
    print("# Validación de extracción (estaciones 4 y 5, en sesión)\n")
    for pid, ficha in EXTRACTED.items():
        res = extract.validate_extraction(ficha)
        adv = adversarial.evaluate(ADVERSARIAL[pid])
        print(f"## {pid}")
        print(f"  estación 4 (extracción): {'ACEPTADA' if res.accepted else 'RECHAZADA'}"
              f"{'' if res.accepted else ' — ' + res.reject_reason}")
        if res.dropped_fields:
            print(f"    numéricos sin cita → null: {res.dropped_fields}")
        print(f"  estación 5 (adversaria): {adv.veredicto.upper()} — {adv.razon}")
        if adv.failed_axes:
            print(f"    ejes marcados: {adv.failed_axes}")
        print()


if __name__ == "__main__":
    main()
