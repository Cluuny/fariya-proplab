## 1. Retornos seguros ante huecos

- [x] 1.1 `engine._asset_returns`: `ffill` del precio por columna antes de `pct_change` (día no cotizado → 0; retorno cruzado → reapertura)

## 2. Guard sobre calendarios desalineados

- [x] 2.1 `tests/test_lookahead.py`: `_misaligned_prices` (un instrumento con ~15% de días faltantes); cheat→Sharpe>5, honest→<2 sobre datos desalineados
- [x] 2.2 Test: el retorno que cruza un hueco no se pierde y se atribuye a la reapertura (día del hueco=0)

## 3. Procedencia del anclaje

- [x] 3.1 `SHARPE_REFERENCE.source`: citar la corroboración (Wikipedia closing-milestones, fecha de consulta) y anotar el pendiente (cierre diario independiente exacto)

## 4. Política de holdout (§3.5)

- [x] 4.1 `hypotheses/HOLDOUT.md`: política + exención explícita de H001 + desde cuándo rige
- [x] 4.2 `config.HOLDOUT_START` (últimos 3 años)

## 5. Reporte (higiene de auditabilidad)

- [x] 5.1 Corregir el arrastre de copy: §3 dice "0.75 ± 0.15" (viejo) → 0.80 ± 0.10; banner y "Correcciones de esta rev." con el número/tema correctos (PR #10, gap-safe)
- [x] 5.2 Añadir la nota de la política de holdout (H001 exenta) al reporte

## 6. Cierre

- [x] 6.1 Toda la suite pasa (`uv run pytest`)
- [x] 6.2 Commit
