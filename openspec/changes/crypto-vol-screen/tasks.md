# Tasks
## 1. Bloque 1 — ingesta Deribit
- [x] 1.1 Verificar cobertura API pública ANTES de construir (DVOL sí; cadena de opciones histórica no)
- [x] 1.2 Series diarias: IV(DVOL), RV, prima IV−RV; skew/estructura NO construibles gratis (documentado)
- [x] 1.3 Calidad (huecos/absurdos, KILL >25%)
## 2. Bloque 2 — amplitud
- [x] 2.1 N_eff spot / vol / combinado + aporte marginal por serie (participation ratio)
## 3. Bloque 3 — IC de la prima
- [x] 3.1 IC con IC95 bootstrap por bloques; dos objetivos (carry vs timing); obs independientes
- [x] 3.2 Colas (skew/curtosis) — cola izquierda del short-vol
## 4. Bloque 4 — criterio comprometido
- [x] 4.1 IR = IC·√(12·N_eff) vs 0.65; veredicto INDETERMINADO
- [x] 4.2 D5 expectativa cumplida/refutada
## 5. Bloque 5 + entregable
- [x] 5.1 Advertencia del suelo de costes de opciones (documentada, sin resolver)
- [x] 5.2 docs/crypto_vol_screen.md D1-D5
## 6. Verificación
- [x] 6.1 Sin ficha/pre-registro; holdout intacto; test verde
