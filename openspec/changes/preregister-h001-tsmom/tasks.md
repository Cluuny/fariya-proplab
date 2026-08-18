## 1. Escribir la ficha de pre-registro

- [x] 1.1 Crear `hypotheses/H001_tsmom.yaml` con el esquema §7.1: `id`, `fuente` (tipo/cita/url/fecha_publicacion), clasificación (`familia`, `mecanismo`, `explicacion_economica`, `estructura`, `direccionalidad`)
- [x] 1.2 Operabilidad: `instrumentos` (los 9), `n_instrumentos: 9`, `frecuencia_datos: diaria`, `horizonte_holding_dias`, `datos_requeridos: [precio_ohlc]`, `operable_en_prop: true`, `razon_si_no: null`
- [x] 1.3 Resultado original + evidencia externa: `periodo_original: "1965-2009"`, `sharpe_reportado: 1.2` (con nota "no es nuestro listón"), `veredicto_externo`, `replicaciones_encontradas`
- [x] 1.4 Hipótesis testeable: `hipotesis`, `regla_entrada` (long si ret_12m>0, short si <0), `regla_salida` (rebalanceo mensual), `sizing` (inverso-vol con rolling_vol + escalado global a 8% vol de portafolio, ≤ max_gross), `universo_test`, `holdout: exento` (con razón), `metrica_exito: Sharpe neto > 0.4`, `FALSADOR: Sharpe neto < 0.2 → muerta, sin variantes`
- [x] 1.5 Gestión de cola: `estado: pre_registrado`, `intentos_realizados: 0`, `fecha_test: null`
- [x] 1.6 Comentarios que dejen claras las adaptaciones vs el paper (9 instrumentos no 58; período casi todo post-2010; lookback en meses de calendario; swap sin dirección conservador; sizing a 8% de portafolio)

## 2. Cierre

- [x] 2.1 Verificar que el YAML es válido (parsea) y que el FALSADOR y la hipótesis están completos
- [x] 2.2 Commit del pre-registro ANTES de cualquier código de señal
