# PropLab — a verdict factory for trading strategies (CLOSED)

**What it is.** A research/backtesting system that turns a written trading hypothesis into a
measured, falsifiable number — under a committed cost floor and a pre-registered falsifier —
so ideas are killed by arithmetic before risking capital.

**What it measured.** Two cycles (CFD spot, then crypto perps), **nine strategy families**, each
with a pre-registered falsifier and a measured verdict; plus a blind research pipeline (91
candidates) and a terrain-breadth screen (effective number of independent bets, N_eff, across
every accessible universe).

**What it concluded.** **Zero survivors.** No accessible universe ($125/mo budget) has the
*breadth* for any signal to clear the floor: crypto (free, unlimited) N_eff **2.16**, the widest
accessible (CME futures, ~$50/mo) **8.15**, IR ceiling ~**0.14** vs a required **0.64**. The nine
deaths were **one structural constraint — breadth — manifesting nine times**, not nine independent
failures. Own findings recorded: ĉ≈2.5-3.0 in crypto microstructure, trade imbalance not subsumed,
profile levels not redundant (26%); and an independent paper (arXiv 2608.21888) replicates the
same cost-beats-signal wall. Full verdict: **`docs/program_verdict.md`**.

**Reopening.** Only if an objective condition in **`docs/reopening_conditions.md`** is met
(N_eff ≥ 14, a revised/accepted lower objective, or a measured IC ≥ 0.10) — cited with the number.

**Reproduce.** `uv sync` then: `uv run pytest` (237 tests), `uv run python -m scripts.terrain_breadth`
(the breadth screen), `uv run python -m scripts.effective_breadth` (CFD N_eff). Verdicts and data
provenance live in `docs/` and `hypotheses/`; raw binaries are gitignored (regenerable).

---

## Architecture

```
prop-lab/
├── data/{raw,clean}/      # Dukascopy dumps (immutable) → parquet (derived); crypto in data/raw_crypto
├── src/
│   ├── config.py          # instruments, costs, Sharpe reference
│   ├── signals.py         # PURE functions: prices → target weights
│   ├── engine.py          # weights → net returns with costs (single cost point)
│   ├── costs_model.py     # cost floors (CFD / futures / crypto / intraday)
│   └── pipeline/          # Flujo 2: discover → operability → costs → extract → adversarial → gate
├── hypotheses/            # pre-registration + falsifier + verdict (QUEUE.md = final state)
├── docs/                  # program_verdict.md, terrain_breadth.md, reopening_conditions.md, run reports
└── tests/
```

## Hard rules

- `data/raw*/` is immutable; every clean output is derived and regenerable.
- `signals.py` are pure functions (stateless, no I/O, `sum(|weights|) <= 1`).
- `engine.py` is the only module that applies costs.
- Keyword decision gates use word-boundary matching (`\b`); every report is regenerable.
- The holdout (`config.HOLDOUT_START`) is touched only by a hypothesis that passed in-sample.

See `PropLab_Documento_Maestro.pdf` for the original thesis and plan.
