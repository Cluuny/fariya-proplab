## 1. Runner (in-sample, holdout intacto)

- [x] 1.1 `scripts/run_h007.py`: reusa `signals.tsmom` sin cambios sobre los 17; corta en 2023-08-16 (assert holdout intacto)
- [x] 1.2 Dos muestras (A 2005→, B 2015→); BRUTO y NETO por separado; swaps 0.0/0.3/1.0
- [x] 1.3 Calibración: baseline period-matched (H001 a 2023-08-16) para evitar el confound de período
- [x] 1.4 Dos lecturas independientes: calibración (bruto) vs falsador (neto)

## 2. Registrar y cerrar

- [x] 2.1 Veredicto en la ficha (estado muerta, bruto/neto separados, hallazgo de calibración) sin tocar campos congelados
- [x] 2.2 `results/H007/report.md` + `QUEUE.md`
- [x] 2.3 Suite verde; commit
