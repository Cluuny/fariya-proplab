## 1. Correcciones a la ficha (pre-ejecución)

- [x] 1.1 `holdout: exento → respetado` + razón (grado de libertad de selección de universo) + `holdout_detalle` (in-sample → 2023-08-16)
- [x] 1.2 Muestras A (2005 → 2023-08-16) y B (2015 → 2023-08-16); `metrica_exito`/`FALSADOR` in-sample
- [x] 1.3 `n_eff` explícito (5.32 con 17; 5.20 con 18; 3.73 con 9); factor √(5.32/3.73)=1.194; `bruto_esperado` [0.29, 0.37]
- [x] 1.4 `intentos_familia_convencion` (deflated N=5 tras esta corrida); `enmiendas` pre-ejecución
- [x] 1.5 `QUEUE.md` actualizado

## 2. Cierre

- [x] 2.1 YAML parsea; sigue `pre_registrado`, `intentos_realizados: 0`
- [x] 2.2 Commit (sin correr; la ficha ya se puede implementar)
