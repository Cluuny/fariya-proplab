## 1. Corrección del framing de duty
- [x] 1.1 `costs_model.sharpe_activo_requerido` = 0.40/√duty + 0.245 (duty bajo SUBE el listón)
- [x] 1.2 Corregir `data/cot_coverage.md` y `docs/queue_triage.md`; H002 motivo principal = concentración
## 2. Cribado condicional
- [x] 2.1 `scripts/cot_screen.py`: Sharpe activo del fade por instrumento y agrupado, IC 95%
- [x] 2.2 n efectivo por EPISODIOS; bootstrap POR EPISODIO; verificación del signo del mecanismo
- [x] 2.3 Expectativa comprometida y criterio de decisión escritos ANTES en `docs/cot_diagnostic.md`
## 3. Cierre
- [x] 3.1 Veredicto: Sharpe activo ~0 < 0.7 → COT muere sin pre-registro; QUEUE actualizado
- [x] 3.2 Test; suite verde; commit (H008 NO se escribe)
