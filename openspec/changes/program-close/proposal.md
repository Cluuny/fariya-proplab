# Cierre formal del programa (con las cuatro confirmaciones)

## Why

El primer cierre formal (change program-close previo, tag v1.0-closed) precedió a los dos análisis
del ciclo de fondeo (economía del payout y sensibilidad a la volatilidad). El veredicto ahora
descansa en CUATRO confirmaciones independientes, no dos; el documento final debe presentarlas
juntas y quedar autosuficiente dentro de un año.

## What Changes

1. **`docs/program_verdict.md` — versión final autosuficiente:**
   - Sección nueva «Las CUATRO confirmaciones independientes del cierre» (tabla): suelo de costes
     (§1.2, 0.64 req vs 0.37), amplitud (§1.7, N_eff 8.15 vs 14), economía del payout (§1.8,
     0.50-0.80 req vs 0.32-0.37), volatilidad (§1.9, óptimo 8%, EV $3.3k/año a 0.37).
   - §1.8 NUEVA (economía del payout) y §1.9 NUEVA (volatilidad, con la AUTOCORRECCIÓN del
     P(quemar)≈0 como ejemplo de que el sistema corrige sus propias conclusiones). Relectura
     renumerada a §1.10.
   - Ya presentes: las 9 familias (§1.1), la relectura (§1.10, una restricción con nueve caras),
     los hallazgos propios (§1.3/§1.3b: ĉ 2.5-3.0, TI no subsumido, perfil no redundante 26%,
     N_eff cripto 2.16), la validación externa (§1.6, arxiv:2608.21888).
2. **`hypotheses/QUEUE.md`:** banner de cierre actualizado a las cuatro confirmaciones + «ninguna
   condición de reapertura se cumple hoy».
3. **`README.md`:** diez líneas — conclusión reescrita a las cuatro confirmaciones.
4. **Tag `v1.1-closed`** en git (versión final más completa; v1.0-closed queda como historia).
5. **`docs/reopening_conditions.md`:** sección nueva «Estado HOY» — las tres condiciones con su
   número medido, verificando que NINGUNA se cumple (C1 N_eff 8.15<14; C2 objetivo sin revisar; C3
   IC nunca ≥0.10).

## Impact

- MOD: `docs/program_verdict.md` (§1.8/§1.9 nuevas, §1.10 relectura, tabla de 4 confirmaciones),
  `hypotheses/QUEUE.md`, `README.md`, `docs/reopening_conditions.md` (estado hoy).
- Tag git `v1.1-closed`.
- Sólo documentación; holdout intacto; sin pre-registro.
