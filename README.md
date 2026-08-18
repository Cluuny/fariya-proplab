# Prop Lab

Research and backtesting system for swing trading on prop-firm funded accounts.
A verdict factory: turns a written hypothesis into a measured number —
`P(pasar el challenge)` — repeatably.

See `PropLab_Documento_Maestro.pdf` for the thesis, the conceptual framework and the plan of attack.

## Architecture (section 3.3 of the master document)

```
prop-lab/                 # this root IS prop-lab (no subfolder)
├── data/
│   ├── raw/              # Dukascopy dumps, IMMUTABLE, never touched
│   └── clean/            # parquet, one file per instrument (derived)
├── src/
│   ├── config.py         # instruments, costs, Sharpe reference
│   ├── loaders.py        # raw → clean + quality validation
│   ├── signals.py        # PURE functions: prices → target weights (contract with Flow 2)
│   ├── engine.py         # weights → net returns with costs (single cost point)
│   ├── challenge.py      # returns → P(pass)  ← CORE (stub; Block B)
│   └── report.py         # everything → reproducible HTML/markdown
├── hypotheses/           # pre-registration + falsifier + verdict (future phases)
├── notebooks/            # throwaway exploration
├── results/              # one directory per hypothesis, immutable
└── tests/
```

## Hard rules

- `data/raw/` is immutable: every clean output is derived and regenerable.
- `signals.py` are pure functions (stateless, no I/O, `sum(|weights|) <= 1`).
- `engine.py` is the only module that applies costs.
- Every report is regenerable with a single command (full reproducibility).

## Usage

```bash
uv sync                    # install dependencies
python -m src.loaders      # raw → clean parquet + quality report
uv run pytest              # tests
```

## Status

Block A (weeks 1-3): data + engine + report. `challenge.py`, the real
hypotheses and Flow 2 (research) arrive in later changes.
