## Context

Ver `proposal.md`. `src/loaders.py:129 _detect_contract_jumps(returns, sigma)` corre `z = (returns-mean)/std` sobre los MISMOS retornos close-to-close y el MISMO `sigma` que la detección de `anomalous_return` (`validate`, línea ~173), así que ambos marcan idéntico conjunto → doble conteo.

## Goals / Non-Goals

**Goals:** que `contract_jump` sea una señal distinta (gap overnight), sin doble conteo; verificación en código de los datos reales.

**Non-Goals:** corregir/ajustar los gaps (sólo se marcan para revisión humana); un calendario de rollover por instrumento (no disponible); cambiar las demás validaciones.

## Decisions

### D1 — `contract_jump` = gap de apertura entre sesiones
`_detect_contract_jumps(df, sigma)` calcula el gap `g_t = log(open_t / close_{t-1})`, lo z-scorea y marca `|z| > sigma`. Es ortogonal al retorno close-to-close `log(close_t/close_{t-1})` que ya cubre `anomalous_return`. Un rollover de futuros/CFD se ve típicamente como un hueco de apertura, no necesariamente como un retorno intradía-a-intradía anómalo. **Requiere** columna `open`; si falta, devuelve vacío (no re-marca los retornos). **Alternativa:** umbral distinto sobre los mismos retornos — descartada: seguiría midiendo lo mismo, sólo con otro corte.

### D2 — Verificación en código de los datos reales (skip si ausentes)
`tests/test_real_data.py` se salta si `data/clean/` no tiene parquets (los datos están gitignorados; en un clon fresco no existen). Cuando existen, verifica: (a) los 10 instrumentos del universo tienen parquet; (b) el buy&hold de `SHARPE_REFERENCE.instrument` reproduce `SHARPE_REFERENCE.value` dentro de `SHARPE_REFERENCE.tolerance` sobre datos reales (verificación del motor = hito 2); (c) `validate` marca al menos un `anomalous_return` en el histórico de una FX major (evento real de mercado). Es la "forma de verificarlo en código" de lo que el reporte afirma.

## Risks / Trade-offs

- **Datos sin columna `open`** (algún formato/fuente) → `contract_jump` no detecta nada (degradación elegante), documentado.
- **El test de datos reales depende de datos gitignorados** → se salta limpiamente si faltan; no rompe CI ni clones frescos.

## Open Questions

- Umbral específico para gaps de apertura (¿mismo `sigma` que retornos, u otro?): se usa el mismo `sigma` por simplicidad; ajustable si produce demasiados/pocos flags al revisar el histórico real.
