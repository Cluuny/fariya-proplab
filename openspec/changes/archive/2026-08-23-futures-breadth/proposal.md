## Why

Completar el caso de futuros: amplitud estimada (criterio 2) y precio real, y emitir el veredicto GO/NO-GO contra el criterio comprometido.

## What Changes

- **`docs/futures_case.md`** — secciones Bloque 2 (amplitud) y Bloque 3 (precio + veredicto).
- **Bloque 2**: universo proxy con ETFs gratis (Yahoo: rates SHY/IEF/TLT, energía USO/UNG, commod/agri DBC/DBA; `data/proxies/*.csv`) SÓLO para correlación (limitación documentada: tracking error infla N_eff). N_eff 5.31 → 6.14 (+rates) → 7.10 (+energía) → **7.68** (completo). Marginal por clase: rates +0.84, energía +0.98, agri +0.76 — información nueva, NO recombinaciones (confirma breadth-lessons). Techo ×1.20.
- **Bloque 3**: precios EOD (Norgate ~$50/mes ≈152k COP, Barchart, etc.; NO Databento). ~1/10 de un challenge ($500). VEREDICTO: **(1) 0.424<0.50 SÍ, (2) 7.68>7.5 SÍ → GO**, pero frágil: (2) pasa por 0.18 sobre un techo optimista (ETFs inflan), y ninguna familia accesible produce 0.42 de bruto (edge sin resolver). Decisión de bajo arrepentimiento: 1 mes de Norgate para re-verificar N_eff con continuos reales.

## Capabilities

### New/Modified Capabilities
<!-- Ninguna: análisis + doc. skip_specs=true. -->

## Impact

- `docs/futures_case.md` (completo), `data/proxies/*.csv` (ETFs, referencia). Sin código. Veredicto GO frágil, verificable con 1 mes de datos.
