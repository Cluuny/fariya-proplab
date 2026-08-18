## 1. Scaffolding del repositorio

- [x] 1.1 Crear la estructura plana en la raíz (NO subcarpeta `prop-lab/`): `data/raw/`, `data/clean/`, `src/`, `hypotheses/`, `notebooks/`, `results/`, `tests/`, con `.gitkeep` en las carpetas de datos/resultados vacías
- [x] 1.2 Inicializar proyecto Python con `uv` (`pyproject.toml`), fijar Python 3.14, añadir deps `pandas` y `numpy` (marcar `polars` como opcional)
- [x] 1.3 Crear `src/__init__.py` y stubs vacíos con docstring de contrato para `src/loaders.py`, `src/signals.py`, `src/engine.py`, `src/report.py` y `src/challenge.py` (este último sólo stub `raise NotImplementedError`, fuera de alcance)
- [x] 1.4 Añadir `.gitignore` (ignorar `data/clean/`, `results/`, artefactos de `uv`/venv; **no** ignorar `data/raw/`) y un `README.md` breve con la arquitectura de la sección 3.3
- [x] 1.5 Añadir módulo de configuración explícita (`src/config.py` o similar): lista de los 10 instrumentos, parámetros de costo por instrumento (comisión, spread), y fuente + ventana + tolerancia del Sharpe de referencia (decisión D6)

## 2. Capa de datos — `loaders.py` (data-pipeline)

- [x] 2.1 Implementar lectura de dumps crudos desde `data/raw/` sin modificarlos (inmutabilidad, D2)
- [x] 2.2 Implementar limpieza y escritura a parquet: un archivo por instrumento en `data/clean/`, indexado por fecha ascendente, sin duplicados
- [x] 2.3 Implementar validaciones de calidad: gaps de calendario, precios en cero/no positivos, fechas duplicadas, retornos >5σ, feriados mal marcados, saltos por cambio de contrato — registrando instrumento, fecha y tipo
- [x] 2.4 Implementar el reporte de calidad legible por instrumento (rango de fechas, nº observaciones, días faltantes, conteo por tipo de anomalía); por defecto markdown
- [x] 2.5 Exponer punto de entrada `python -m src.loaders` que produce parquets + reporte y termina sin error
- [x] 2.6 Tests: inmutabilidad de `raw/`, regeneración determinista, un parquet por instrumento, y detección de cada tipo de anomalía sobre datos sintéticos

## 3. Contrato de señal — `signals.py` (signal-contract)

- [x] 3.1 Definir el contrato de función de señal (typing `Protocol`): `(prices, ...) -> DataFrame de pesos` indexado por fecha, una columna por instrumento
- [x] 3.2 Implementar un validador reutilizable del invariante `sum(|pesos|) <= 1` por fecha, que identifique fechas infractoras
- [x] 3.3 Implementar la señal de referencia buy & hold conforme al contrato (pesos constantes)
- [x] 3.4 Tests: pureza/determinismo (misma entrada → misma salida, entradas sin mutar), forma de salida, y rechazo/aceptación del invariante de exposición

## 4. Motor de backtest — `engine.py` (backtest-engine)

- [x] 4.1 Implementar el cálculo de retornos brutos a partir de pesos objetivo y precios
- [x] 4.2 Aplicar costos (comisión, spread, slippage, impacto) como único punto de costos del sistema (D4), leyendo parámetros de `config`
- [x] 4.3 Garantizar determinismo (mismas entradas → mismos retornos), sin estado externo
- [x] 4.4 Test de verificación: buy & hold sobre un índice reproduce su Sharpe histórico conocido dentro de la tolerancia de `config`
- [x] 4.5 Tests: los costos reducen el retorno vs. bruto; buy & hold sin rotación no incurre costos de transacción posteriores a la entrada

## 5. Capa de reporte — `report.py` (reporting)

- [x] 5.1 Implementar cálculo de métricas: equity curve, Sharpe, max drawdown, distribución de retornos
- [x] 5.2 Implementar emisión del reporte en formato legible (HTML o markdown) de forma determinista
- [x] 5.3 Exponer un único comando que regenera el reporte completo desde una estrategia dada (p. ej. buy & hold)
- [x] 5.4 Tests: el reporte contiene las métricas mínimas y es determinista (mismas entradas → mismos valores)

## 6. Verificación de extremo a extremo (Definition of Done)

- [x] 6.1 `python -m src.loaders` corre limpio y produce reporte de calidad de datos
- [x] 6.2 El motor reproduce el Sharpe conocido de buy & hold dentro de tolerancia
- [x] 6.3 `report.py` genera el reporte con un solo comando
- [x] 6.4 Configurar `run_tests` en `openspec/config.yaml` (p. ej. `uv run pytest`) y confirmar que la suite pasa
- [x] 6.5 Commit del hito de Semana 1–3 (datos limpios + motor verificado + reporte)
