# Tasks

## 1. Cribado aritmético del candidato (sin backtest)
- [x] 1.1 `candidate_screen.py`: sharpe_se/ci, expected_max_sharpe (Deflated, Bailey-LdP), effective_breadth (+tests)
- [x] 1.2 `scripts/screen_sectoral.py`: los 4 números (deflación, nulo compartido, amplitud/IC, operabilidad)
- [x] 1.3 `docs/candidate_sectoral_screen.md`: veredicto cribado_muere con los 4 números; corrección honesta de (1.4)

## 2. Refinar es_estrategia_operable
- [x] 2.1 Límite de palabra en el gate positivo (arregla «carry»⊂«carrying», «long the»⊂«along the»)
- [x] 2.2 Rechazo por horizonte inoperable (< 1 min, suelo de costes intradía) + descalificadores meta/tooling
- [x] 2.3 Regresión: 4 falsos positivos de la run 002 mueren en E2.5, sectorial sobrevive (+ run 001 sigue verde)

## 3. Decisión de fuentes documentada (sin ejecutar)
- [x] 3.1 `docs/pipeline_source_decision.md`: caso Quantpedia Premium, densidad medida, a favor/en contra, no decidir

## 4. Verificación
- [x] 4.1 Suite verde; sin pre-registro, sin backtest, holdout intacto, API no cableada
