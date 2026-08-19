## 1. Corregir la ficha (hypotheses/H003_seasonality.yaml)

- [x] 1.1 `fuente`: separar Ariel (1987, JFE) y McConnell-Xu (2008, FAJ), cada una con año y URL
- [x] 1.2 `estadistico_primario` (existencia): contraste de medias TOM vs no-TOM, por instrumento y agrupado, SE por block bootstrap, diff en bps/día + IC 95%; usa toda la muestra
- [x] 1.3 `benchmark_nulo`: mismos índices/sizing/nº días, días aleatorios, 1000 remuestreos semilla fija; distribución del Sharpe nulo (medido: media ~0.24, p95 ~0.65)
- [x] 1.4 `FALSADOR` relativo: TOM debe superar el p95 del nulo; Sharpe absoluto = diagnóstico, no falsador
- [x] 1.5 `metrica_exito` reescrita: existe (contraste significativo) Y explotable (Sharpe neto > p95 nulo)
- [x] 1.6 `poder_estadistico`: SE in-sample 0.30 / holdout 0.59; IC 95% obligatorio; estado `underpowered`; holdout sólo refuta ("consistente", nunca "confirmado")
- [x] 1.7 `sizing`: caveat de recorte → tripwire de bug (apalancamiento esperado ~1.15×)
- [x] 1.8 `resultado_esperado`: reencuadrar (Sharpe absoluto ~0.3-0.5 es beta; el exceso sobre el nulo es lo que importa); `estado` admite `underpowered`; añadir `enmiendas` (pre-ejecución)

## 2. Cierre

- [x] 2.1 Verificar que el YAML parsea y sigue `pre_registrado`, `intentos_realizados: 0`
- [x] 2.2 Commit ANTES de cualquier código de señal
