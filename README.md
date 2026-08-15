# Prop Lab

Sistema de investigación y backtesting para swing trading en cuentas de fondeo.
Fábrica de veredictos: convierte una hipótesis escrita en un número medido —
`P(pasar el challenge)` — de forma repetible.

Ver `PropLab_Documento_Maestro.pdf` para la tesis, el marco conceptual y el plan de ataque.

## Arquitectura (sección 3.3 del documento maestro)

```
prop-lab/                 # esta raíz ES prop-lab (no hay subcarpeta)
├── data/
│   ├── raw/              # dumps de Dukascopy, INMUTABLE, nunca se tocan
│   └── clean/            # parquet, un archivo por instrumento (derivado)
├── src/
│   ├── config.py         # instrumentos, costos, referencia de Sharpe
│   ├── loaders.py        # raw → clean + validación de calidad
│   ├── signals.py        # funciones PURAS: precios → pesos objetivo (contrato con Flujo 2)
│   ├── engine.py         # pesos → retornos netos con costos (único punto de costos)
│   ├── challenge.py      # retornos → P(pasar)  ← NÚCLEO (stub; Bloque B)
│   └── report.py         # todo → HTML/markdown reproducible
├── hypotheses/           # pre-registro + falsador + veredicto (fases futuras)
├── notebooks/            # exploración desechable
├── results/              # un directorio por hipótesis, inmutable
└── tests/
```

## Reglas duras

- `data/raw/` es inmutable: toda salida limpia es derivada y regenerable.
- `signals.py` son funciones puras (sin estado, sin I/O, `sum(|pesos|) <= 1`).
- `engine.py` es el único módulo que aplica costos.
- Todo reporte es regenerable con un comando (reproducibilidad total).

## Uso

```bash
uv sync                    # instalar dependencias
python -m src.loaders      # raw → clean parquet + reporte de calidad
uv run pytest              # tests
```

## Estado

Bloque A (semanas 1-3): datos + motor + reporte. `challenge.py`, las hipótesis
reales y el Flujo 2 (investigación) llegan en changes posteriores.
