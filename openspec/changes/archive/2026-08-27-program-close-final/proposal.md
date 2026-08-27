# Cierre final del registro

## Why

Tras las dos calibraciones pre-run-003, el cierre gana una QUINTA confirmación (el pipeline de
búsqueda no puede converger: 0/91) y un hallazgo estructural POSITIVO que merece registro preciso
(las estrategias sí se diversifican). El documento final debe recogerlos y quedar autosuficiente.

## What Changes

1. **`docs/program_verdict.md`:**
   - **§1.10 NUEVA — La quinta confirmación:** el pipeline no puede converger. 0 supervivientes de
     91; cota superior 95% de la tasa = 3.3%; ~120 candidatos para UN superviviente esperado, ×4 +
     familias distintas; con el estimador puntual (0), ningún N finito da supervivientes. La parada
     de 200 estaba infradimensionada. El programa se cierra por TASA, no por agotamiento.
   - **§1.11 NUEVA — El hallazgo estructural positivo:** las estrategias SÍ se diversifican (ρ media
     0.09, N_eff 2.95 de 3), a diferencia de los instrumentos (ρ 0.7-0.8). Combinar familias
     multiplica el BR como predice la teoría. **El cuello nunca fue combinar; fue producir la
     primera.** Va a favor y aun así no salva el programa.
   - Tabla de confirmaciones CUATRO → CINCO; relectura renumerada a §1.12; cross-refs.
2. **`hypotheses/QUEUE.md`:** banner a cinco confirmaciones; contador 91/200 cerrado por TASA.
3. **`README.md`:** diez líneas — cinco confirmaciones + el hallazgo positivo.
4. **`docs/reopening_conditions.md`:** las tres condiciones con su número actual — C1 N_eff 8.15,
   C2 IC 0.077 (H002), C3 objetivo bajado a 0.20 sigue sin despejar; ninguna se cumple.
5. **Tag `v1.2-closed`** (v1.0/v1.1 quedan como historia).

## Impact

- MOD: `docs/program_verdict.md` (§1.10/§1.11 nuevas, §1.12 relectura), `hypotheses/QUEUE.md`,
  `README.md`, `docs/reopening_conditions.md`.
- Tag git `v1.2-closed`. Sólo documentación; holdout intacto; sin pre-registro.
