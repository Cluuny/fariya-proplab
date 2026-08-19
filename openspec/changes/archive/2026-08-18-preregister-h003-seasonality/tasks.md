## 1. Escribir la ficha (hypotheses/H003_seasonality.yaml)

- [x] 1.1 Esquema §7.1: `id: H003`, `fuente` (Ariel 1987 / McConnell-Xu 2008), clasificación (`familia: seasonality`, `mecanismo: institucional`, `explicacion_economica`, `estructura: seasonality`, `direccionalidad: long_only`)
- [x] 1.2 Operabilidad: `instrumentos: [SPX500, GER40, JPN225]`, `n_instrumentos: 3`, `frecuencia_datos: diaria`, `horizonte_holding_dias: ~4`, `datos_requeridos: [precio_ohlc]`, `operable_en_prop: true`
- [x] 1.3 Resultado original + evidencia externa (confirmado, atenuado post-2000)
- [x] 1.4 Hipótesis testeable: `hipotesis`, `regla_entrada` (long en ventana [−1,+3]), `regla_salida` (flat al 3er día), `sizing` (vol-inversa ex-ante 8% portafolio, ≤ max_gross, caveat flat-time), `metrica_exito` (Sharpe in-sample > 0.4), `FALSADOR` (< 0.2)
- [x] 1.5 Holdout RESPETADO: `holdout: respetado`, in-sample 2011-09→2023-08-16, holdout 2023-08-17→2026 reservado
- [x] 1.6 `resultado_esperado` (Grinold-Kahn, central ~0.35, desviaciones), `zona_marginal` (chequeo único ventana [−1,+4], deflated Sharpe), `sensibilidad_costos` (swap primario 0.3; spread la fricción real aquí), `diagnosticos_requeridos` (turnover_anual, sharpe_zero_cost, maxdd/vol)
- [x] 1.7 Gestión de cola: `estado: pre_registrado`, `intentos_realizados: 0`, `fecha_test: null`; comentarios con las adaptaciones y la lección de H001

## 2. Cola y cierre

- [x] 2.1 Actualizar `hypotheses/QUEUE.md`: H003 = activa (pre-registrada)
- [x] 2.2 Verificar que el YAML parsea y el FALSADOR/hipótesis están completos
- [x] 2.3 Commit ANTES de cualquier código de señal
