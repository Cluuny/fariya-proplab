## 1. Escribir la ficha

- [x] 1.1 `hypotheses/H007_tsmom_expanded.yaml` (esquema §7.1): id/fuente/clasificación, `relacion_con_H001`, `intentos_familia_trend: 3`
- [x] 1.2 Operabilidad (17 instrumentos = config), regla/sizing/alineación IDÉNTICAS a H001 (señal `tsmom` sin modificar)
- [x] 1.3 Dos muestras ajustadas a cobertura real (A: FX+metales 2005-2026; B: los 17, 2015-2026); sensibilidad al swap; holdout exento
- [x] 1.4 `resultado_esperado` (bruto [0.29,0.36], neto [0.12,0.20], muerta), `FALSADOR` = H001, `zona_marginal` (deflated con N=3)
- [x] 1.5 `calibracion_del_marco` (criterio bruto ∈ [0.25,0.40] → marco predictivo; independiente del falsador), diagnósticos de primera línea
- [x] 1.6 Gestión de cola: `pre_registrado`, `intentos_realizados: 0`, `fecha_test: null`; QUEUE.md actualizado

## 2. Cierre

- [x] 2.1 Verificar que el YAML parsea y el universo coincide con config (17)
- [x] 2.2 Commit — SIN implementar ni correr (la ficha se revisa antes)
