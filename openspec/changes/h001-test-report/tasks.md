## 1. Generación del reporte

- [x] 1.1 `run_h001.py`: capturar la serie de retornos neta (especificación primaria, swap 0.3) por muestra, además del Sharpe
- [x] 1.2 Componer el markdown: veredicto + contrato + tabla muestra×swap + interpretación + detalle por muestra (métricas/equity/drawdown/distribución vía `src/report.py`)
- [x] 1.3 Escribir `results/H001/report.md` (determinista, sin timestamps) y reportar la ruta a stdout

## 2. Cierre

- [x] 2.1 Correr el runner; verificar que el reporte se genera y los números coinciden con el veredicto de la ficha
- [x] 2.2 Suite verde (`uv run pytest -q`)
- [x] 2.3 Commit
