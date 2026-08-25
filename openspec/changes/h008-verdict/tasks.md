# Tasks

## 1. Sellar el veredicto en la ficha (congelar falsador/resultado_esperado)
- [x] 1.1 `estado: muerta`, `intentos_realizados: 1`, `fecha_test` poblada
- [x] 1.2 Sub-bloque `cierre` en `resultado`: veredicto MUERTA + causa (activo -0.067 vs listón 0.961; con fills ≥5bps -0.986) + matiz (murió por la regla de subasta, no por redundancia)
- [x] 1.3 Registrar el nulo como test defectuoso (causa mecánica, condición (3) no discrimina, diseño correcto futuro)
- [x] 1.4 Registrar el sesgo de exclusión del pareado (73 episodios no aleatorios)
- [x] 1.5 Registrar holdout intacto (nunca descargado)
- [x] 1.6 Verificar que FALSADOR y resultado_esperado NO fueron tocados

## 2. Corregir docs/h008_block4.md
- [x] 2.1 D5: "¿el veredicto cambia entre supuestos? SÍ" → NO (magnitud, no veredicto)
- [x] 2.2 D1/D8: quitar "supera al nulo… llevan información"; veredicto MUERTA
- [x] 2.3 D4: nota de nulo defectuoso (geometría rota, no discrimina)
- [x] 2.4 D2: nota de sesgo de exclusión

## 3. docs/program_verdict.md — novena familia
- [x] 3.1 Registrar H008 (auction/volume profile) con veredicto y los dos hallazgos limpios

## 4. Adversario del pipeline — noveno eje
- [x] 4.1 Añadir eje `nulo_preserva_geometria` a `ATTACK_QUESTIONS`
- [x] 4.2 Actualizar test del adversario (findings dict con la nueva clave)

## 5. Verificación
- [x] 5.1 Suite de tests verde
- [x] 5.2 Actualizar `hypotheses/QUEUE.md` (H008 → MUERTA)
