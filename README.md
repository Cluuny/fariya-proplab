# PropLab — a verdict factory for trading strategies

> **For an AI agent reading this repo:** this README is a *surgical map of the code*. It tells you
> the mental model, the data flow, the hard contracts between modules, and exactly which file/symbol
> owns each responsibility — enough to reason about or modify the code without opening every file.
> For the full audited narrative (every claim with `file:line`), read **`docs/RECAP.md`**.

**What this is.** A research/backtesting system that turns a written trading hypothesis into a
measured, falsifiable number, under a committed cost floor and a pre-registered falsifier. Its job is
**not** to find strategies — it is to *kill each idea by the correct reason, cheaply, before risking
capital*.

**Program state: CLOSED** (git tag `v1.2-closed`). Two cycles (CFD spot, crypto perps), nine strategy
families, zero survivors, confirmed from five independent axes (cost floor, breadth, payout economics,
volatility, pipeline convergence). The code is fully live and tested; what's closed is the *search*,
because the accessible terrain lacks the breadth to clear the cost floor. See `docs/program_verdict.md`
and `docs/reopening_conditions.md` (three objective conditions to reopen).

---

## The mental model (read this first)

There are **two flows**, sharing one engine and one config:

```
FLOW 1 — backtest a KNOWN hypothesis                FLOW 2 — the research pipeline (find hypotheses)
──────────────────────────────────────             ────────────────────────────────────────────────
 data/raw/  (Dukascopy, immutable)                   E1 discover   src/pipeline/discover.py   (arXiv/RSS)
   │  src/loaders.py  (clean + quality)               │
   ▼                                                  E2 operability src/pipeline/triage_operability.py
 data/clean/*.parquet                                 │  E2.5 is-strategy + estimate  estimate.py
   │  src/signals.py  (prices → weights, PURE)        │  E3 costs     src/pipeline/triage_costs.py
   ▼                                                  │  (E4 extract / E5 adversary — in-session)
 src/engine.py  (weights → NET returns; ONLY          │  E7 human gate  src/pipeline/human_gate.py
   │             module that applies costs)           ▼
   ▼                                                 an approved candidate becomes a Flow-1 hypothesis
 src/challenge.py  (returns → P(pass challenge))     state lives in a SQLite queue: src/pipeline/db.py
```

**The three hard contracts** (violating any of them is a bug, enforced by tests):

1. **`data/raw*/` is immutable.** Every `data/clean/` output is *derived and regenerable*. Never edit raw.
2. **`signals.py` are PURE functions** `prices: DataFrame → weights: DataFrame`: stateless, no I/O, and
   on every date `sum(|weights|) ≤ config.MAX_GROSS_EXPOSURE` (`signals.check_exposure`,
   `signals.validate_weights`). Sizing is *ex-ante* (rolling scalar with `.shift(1)`) — **no look-ahead**.
3. **`engine.py` is the ONLY module that applies costs.** One cost point, so a cost change is one edit.

Two more invariants the whole program is built on:
- **The holdout is sacred.** `config.HOLDOUT_START` (2023-08-17, last ~3 years) is touched *only* by a
  hypothesis that already passed in-sample. Most families never touched it.
- **No hidden knobs.** Any parameter that silently decides an outcome is a defect. Provisional params
  are marked as such (e.g. `costs_model.FACTOR_DEGRADACION`), and `challenge.optimal_leverage` stays
  `None` until its objective is defined — an honest absent value beats a wrong one.

---

## Module map (`src/`) — who owns what

| module | responsibility | key public symbols |
|---|---|---|
| **`config.py`** | single source of truth: universe, costs, firm rules, sim params | `INSTRUMENTS` (17), `CostModel`, `COSTS`, `FirmRules`/`DEFAULT_FIRM_RULES`, `SimulatorParams`/`DEFAULT_SIM_PARAMS`, `HOLDOUT_START`, `MAX_GROSS_EXPOSURE`, `BROKER_MARGIN_MULT`, `SHARPE_REFERENCE`, swap calibration (`_MARGIN_FX`, `TRADING_DAY_SWAP_FACTOR`) |
| **`loaders.py`** | raw → clean + quality validation | keeps Mon–Fri only (`:126`, weekend gap captured Fri→Mon close-to-close); `_detect_session_gaps` (overnight gap ≠ anomaly); KILL if >25% missing |
| **`dukascopy.py`** | automatic EOD bar ingestion from Dukascopy | fetch/parse daily bars |
| **`signals.py`** | the Flow-2 boundary: `prices → target weights`, pure | `tsmom` (trend, H001/H007), `tom_seasonal` (seasonality, H003), `buy_and_hold`; `check_exposure`, `validate_weights`; `_long_inverse_vol` (shared ex-ante inverse-vol sizing) |
| **`engine.py`** | `weights → net returns`; the single cost point | `backtest(prices, weights, *, costs, carry_matrix, apply_costs)`; `_asset_returns` (calendar-gap-safe, `:21`); `rolling_vol` (gap-safe, `:120`); `sharpe`, `bars_per_year` |
| **`costs_model.py`** | the cost floor as a *decision tool* | `annual_cost` (`:36`, margin ≈92%); `sharpe_bruto_requerido_duty` (`0.24·duty+0.40` → CFD 0.64 / futures 0.42); `sharpe_activo_requerido` (`0.40/√duty+0.245`); `FACTOR_DEGRADACION=0.35` + `bruto_efectivo` (reported→realized haircut) |
| **`challenge.py`** | **THE CORE**: `returns → P(pass)` as a first-passage problem | `simulate_challenge(returns, *, rules, params, leverage) → ChallengeResult`; `block_bootstrap`; three-outcome accounting `PASSED/FAILED/UNRESOLVED`; guard `p_unresolved>5% → nan`; `optimal_leverage=None`; `analytic_pass_probability` (closed-form oracle, `:368`) |
| **`rates.py`** | historical policy rates → time-varying signed carry | `carry_matrix(index, instruments)` (BIS WS_CBPOL, daily, signed) |
| **`cot.py`** | CFTC Commitments of Traders — first non-price source | positioning series for the COT screen |
| **`report.py`** | reproducible HTML/markdown reports | one command regenerates a report |

### `src/pipeline/` — Flow 2, the research pipeline (7 stations + support)

| module | station / role | key symbols |
|---|---|---|
| **`db.py`** | structured SQLite queue (NOT a RAG): `SELECT … WHERE estado='en_cola' ORDER BY score_prioridad DESC` | `SCHEMA` (table `hipotesis`), `upsert`, `next_in_queue`, `count_processed`, `N_CONDICION_PARADA=200`, vocabularies (`FAMILIAS_DE_RIESGO`, `CAUSAS_DE_MUERTE`, `ESTADOS`) |
| **`discover.py`** | **E1** discovery (monthly cron) | `fetch_arxiv` (q-fin PM/ST/TR + microstructure AND-scope), `fetch_rss` (Alpha Architect/CXO/Quantpedia), `manual_candidate` (SSRN/Reddit/…); pure parsers, isolated network |
| **`triage_operability.py`** | **E2** operability heuristic (deterministic keywords) | `triage_operability` — rejects non-falsifiable (ICT/SMC), cross-sectional equity, options, fundamentals, no-rule, over-budget; `_hits_word` (word-boundary, no substring bugs) |
| **`estimate.py`** | **E2.5** is-it-a-strategy + estimate the fields E3 needs | `is_operable_strategy` (10th axis: position+horizon, not method/theory), `estimate_fields`, `extract_bruto_estimado` (Sharpe / IR / ret-vol / t-stat), `estimate_familia_de_riesgo`, `priority_score` |
| **`triage_costs.py`** | **E3** cost arithmetic (kills most) | `triage_costs` — `bruto_efectivo = reportado × 0.35` vs required (CFD/futures/intraday); `UMBRAL_NETO=0.40` net **per strategy** (0.4·√4=0.8) |
| **`extract.py`** | **E4** PDF → ficha, anti-hallucination validation (LLM = seam) | `validate_extraction` (each numeric needs a citation → else null; no falsifier → schema reject); `extract_from_pdf` (seam, `NotImplementedError` without an injected llm) |
| **`adversarial.py`** | **E5** adversary: 11 attack axes (7 critical) | `ATTACK_QUESTIONS`, `evaluate`; several axes were born from our own errors (H003 benchmark-zero, OFI contemporaneous, H008 null-geometry) |
| **`human_gate.py`** | **E7** human gate: surface 3–5, approve ONE | `candidates_for_review`, `approve`, `render` |
| **`stub_gen.py`** | approved candidate → `signals.py` stub (prices→weights contract) | `stub_gen` (engine unchanged) |
| **`candidate_screen.py`** | arithmetic screen of an E3 survivor (no backtest) | `sharpe_se`, `sharpe_ci`, `expected_max_sharpe` (deflated), `effective_breadth` |
| **`learning_report.py`** | SQL learning report (survival by class/source/family) | `report`; density-by-source; `_por_familia_riesgo` (diversification of survivors) |
| **`backfill.py`** | load the 11 known hypotheses as the VALIDATION SET | `load_backfill` (reproduces zero survivors → sanity check) |
| **`papers.py`, `llm_client.py`** | paper loader; LLM seam (env-var credential, never in repo) | `resolve_paper`; the API is documented but NOT wired |

### `src/crypto/` — the crypto cycle (blocks 1–4)

`ingest.py` (data.binance.vision ingestion + immutable manifest) · `quality.py` (KILL if >25% missing)
· `ofi.py` (Order-Flow Imbalance, Cont-Kukanov-Stoikov) · `calibrate.py` (OFI acceptance test) ·
`cost_model.py` (Binance USDⓈ-M perps: maker/taker, avoidable funding) · `decay.py` (predictive-decay
screen that closed order flow) · `volume_profile.py` (VAH/VAL/POC from aggTrades) · `h008_backtest.py`
(H008 conditional strategy, paired branches, null).

---

## How to run

```bash
uv sync                                   # install deps (Python 3.14, numpy/pandas/pyarrow; stdlib-only pipeline)
uv run pytest                             # ~254 tests (the invariants above are enforced here)
uv run python -m src.loaders              # raw → clean parquet + quality report

# Flow 1 — backtest a family:
uv run python -m scripts.run_h001         # TSMOM; likewise run_h003, run_h007

# Flow 2 — the pipeline (deterministic E1–E3 in batch; E4–E5 need an interactive session):
uv run python -m scripts.pipeline discover|triage|report|queue
uv run python -m scripts.pipeline_run_002 --arxiv-max 80 --cap 40 --seed run001.json --json out.json

# The measurements behind the verdict (reproducible):
uv run python -m scripts.terrain_breadth          # N_eff per accessible universe (breadth closure)
uv run python -m scripts.effective_breadth        # CFD N_eff
uv run python -m scripts.family_breadth           # strategy diversification (families ~uncorrelated)
uv run python -m scripts.funded_sharpe_requirement && …funded_vol_sensitivity   # payout & vol closures
uv run python -m scripts.e3_retro run001.json run002.json                        # E3 recalibration retro-test
```

State persists in **`data/pipeline/research.db`** (SQLite, gitignored, regenerable via `backfill`);
`discover` dedupes by id, so an interrupted run resumes without duplicates. The stop-condition counter
lives in the DB (`db.count_processed` / `N_CONDICION_PARADA=200`); it read 91/200 when the program
closed *by rate*, not by exhaustion.

---

## Where the analysis lives (`docs/`, Spanish)

- **`RECAP.md`** — the definitive audit (start here for the full narrative).
- **`pipeline_walkthrough.md`** — the pipeline end-to-end, with three real candidates and its blind spots.
- `program_verdict.md` — the verdict, five confirmations, the by-breadth re-reading.
- `cost_floor.md`, `terrain_breadth.md`, `funded_sharpe_requirement.md`, `funded_vol_sensitivity.md` — the closures.
- `reopening_conditions.md` — the three objective conditions to reopen (none met today).
- `extraction_defects.md`, `candidate_sectoral_screen.md`, `e3_recalibration.md`, `pre_run_003_calibration.md` — method & calibration.
- `pipeline_run_001.md`, `_002.md` — the blind runs.

## Conventions for changing this repo

- **One change = one OpenSpec change** under `openspec/changes/` (proposal + tasks; docs-only changes set
  `skip_specs: true`), on a **feature branch**, via PR (squash-merge), then archived. Never commit to `main` directly.
- **Respect the contracts** (pure signals, single cost point, immutable raw, holdout, word-boundary
  keyword gates). Frozen fichas (`hypotheses/*.yaml` past `fecha_test`) and their falsifiers are immutable —
  append post-execution results, never rewrite the committed falsifier.
- **No hidden knobs, and measure vs the reviewer.** If a number would decide an outcome, expose it and
  calibrate it. Six times in this program a measurement refuted a committed expectation — that is the point.

*(Original thesis and plan: `PropLab_Documento_Maestro.pdf`.)*
