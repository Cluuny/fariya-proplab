# Tareas

## 1. Problema A — Sharpe de exceso (verificación + parámetro rf)
- [x] 1.1 Verificar numéricamente que nuestros retornos ya son de exceso (rf USD avg
  1.44%; restar rf bajaría H007-A neto 0.184 → 0.023 = doble-conteo).
- [x] 1.2 Añadir parámetro `rf` a `engine.sharpe` (default 0.0), con docstring que explica
  por qué el default es correcto (retornos ya de exceso, sin interés sobre colateral).
- [x] 1.3 Test `test_sharpe_default_is_excess_no_double_subtraction` (rf=0 default; rf>0
  baja el Sharpe ≈ rf/vol).

## 2. Problema B — comisiones (bruto de comisiones de la industria)
- [x] 2.1 Documentar que 0.14 de la industria es neto (ret 2.9% / vol 11% → rf implícito
  ≈1.4%); comisión de gestión estándar ~2% ("2 y 20"; rango 1.5–2.5% → Sharpe 0.28–0.37).
- [x] 2.2 Bruto de comisiones ≈ 0.32; comparación correcta 0.32 vs 0.424 (hueco ~30%, no 3×).

## 3. Docs
- [x] 3.1 Actualizar `docs/futures_case.md`: corrección de comparabilidad (exceso + comisiones),
  contraste H007-A vs bruto de industria, nota explícita "el veredicto GO/NO-GO NO cambia".
- [x] 3.2 Actualizar `docs/program_verdict.md`: conclusión 3 con bruto de industria ≈0.32 y
  nota metodológica (nuestros Sharpes ya son de exceso).

## 4. Verificación
- [x] 4.1 `pytest tests/test_engine.py` pasa (incluye el nuevo test).
