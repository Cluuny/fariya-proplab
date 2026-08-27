"""Regresión del décimo eje es_estrategia_operable (E2.5) — corrida 002.

FIXTURE: las 11 fichas que sobrevivieron a E2 en la corrida 001. El eje debe MATAR las 10
que no son estrategias (método/teoría/modelo/monitor) y DEJAR VIVA la de mean reversion
(arxiv:2608.21888), que sí trae una regla operable ('betting against the previous candle').
Es la condición que el bloque de la corrida 002 exige explícitamente.
"""

from __future__ import annotations

from src.pipeline import estimate

# --- generado de docs/pipeline_run_001.md / el volcado de la corrida 001 (abstracts reales) ---
RUN001_SURVIVORS = [
    # arxiv:2608.23416
    ("arxiv:2608.23416", "The Axiomatic Trader: Latent Regularity, Information Budgets, and the Canonical Form of a Quantitative Investment System",
     "Systematic trading rests on one article of faith: that regularities found in the past persist. We state it as a time-invariant mechanism driven by an unobserved latent state, and show that it leaves a researcher five constants to declare --- the recurrence bound $Lambda$ at a block length $b$, the invariance defect $epsilon_0$ of the representation it is declared of, the coherence times $ell_i$ of the state's coordinates, the signal ceiling $rho$ and the fraction $kappa$ of it contingent on the regime --- after which the architecture of a correct quantitative investment system is nearly forced"),
    # arxiv:2608.23808
    ("arxiv:2608.23808", "Equity Strategy Backtesting: Luck or Edge? The MinervaScore as a Statistical Robustness Grade",
     "Backtests of trading strategies are often selected after many parameter trials. A strong historical result can therefore reflect search luck rather than a persistent signal. Standard summaries such as return, Sharpe ratio, and drawdown do not record how many candidates were tried, whether the selected rule survives out-of-sample validation, or whether the available history is long enough to support the result. This paper describes the MinervaScore, a post-selection robustness grade for trading strategies. The score combines four established validation quantities: Deflated Sharpe Ratio, Probabi"),
    # arxiv:2608.20727
    ("arxiv:2608.20727", "A Multiscale Ball Test for Conditional Mean Independence",
     "Tests of conditional mean independence can lose power when departures are confined to a bounded part of a multivariate predictor space and the relevant spatial scale is unknown. We propose a Multiscale Ball Conditional Mean Independence (MBCMI) test that aggregates support-weighted local mean contrasts in an outcome variable across balls centered on each data point in a predictor set. Fixed-grid theory identifies the population target, establishes consistency for grid-visible alternatives, and derives a Pitman local-power limit governed by the ball-smoothed mean departure. For serial data, fea"),
    # arxiv:2608.20179
    ("arxiv:2608.20179", "Dynamic Portfolio Optimization under CVaR Constraints",
     "We study continuous-time dynamic portfolio optimization under a Conditional Value-at-Risk (CVaR) constraint on the investor's terminal loss. For a general class of convex trading objectives, we exploit the auxiliary-threshold representation of CVaR to establish the existence of an optimal strategy and strong duality without requiring market completeness. These results motivate a dual-based nested bisection--golden-search algorithm over the threshold and Lagrangian multiplier, where the inner iterations reduce to standard unconstrained stochastic control problems. We prove that the resulting st"),
    # arxiv:2608.19389
    ("arxiv:2608.19389", "Concentrated Liquidity Provision: a Reinforcement Learning Perspective",
     "Automated market makers (AMMs) are a cornerstone of decentralised finance (DeFi). Constant product markets with concentrated liquidity, such as UniswapV3, are now a well-established design. In these markets, liquidity providers (LPs) face a sequential decision problem: they must decide when to rebalance their positions and which price ranges to allocate capital to as market conditions evolve. We formulate dynamic liquidity provision as a stochastic impulse control problem and use reinforcement learning (RL) to solve it, focusing on providing interpretable solutions. We show that learned polici"),
    # cxo:https-www-cxoadvisory-com-volatility-effects-ups-and-downs-o
    ("cxo:https-www-cxoadvisory-com-volatility-effects-ups-and-downs-o", "Ups and Downs of Leveraged ETFs [PREMIUM]",
     "What are likely outcomes for different kinds of leveraged exchange-traded funds (LETF), which typically use embedded financing and daily rebalancing to target two or three times the daily return of assets they track? In their July 2026 paper entitled &#8220;The Costs and Benefits of Leveraged ETFs&#8221;, Chris Murray and Marco Sammon examine the costs and...... <a href=\"https://www.cxoadvisory.com/volatility-effects/ups-and-downs-of-leveraged-etfs/\" class=\"read-more\">Keep Reading <svg class=\"cxo-icon cxo-icon--angle-double-right\" viewBox=\"0 0 512 512\" fill=\"currentColor\" aria-hidden=\"true\" wi"),
    # cxo:https-www-cxoadvisory-com-equity-premium-do-convertible-bond
    ("cxo:https-www-cxoadvisory-com-equity-premium-do-convertible-bond", "Do Convertible Bond ETFs Attractively Meld Stocks and Bonds? [PREMIUM]",
     "Do exchange-traded funds (ETF) that hold convertible corporate bonds offer attractive performance? To investigate, we compare performance statistics for the following four convertible bond ETFs, three available and one dead, to those for a monthly rebalanced 60%-40% combination of SPDR S&#38;P 500 ETF Trust (SPY) and iShares iBoxx $ Investment Grade Corporate Bond ETF (LQD):...... <a href=\"https://www.cxoadvisory.com/equity-premium/do-convertible-bond-etfs-attractively-meld-stocks-and-bonds/\" class=\"read-more\">Keep Reading <svg class=\"cxo-icon cxo-icon--angle-double-right\" viewBox=\"0 0 512 512"),
    # arxiv:2608.22768
    ("arxiv:2608.22768", "The Loop-Gain Matrix: Coupled Rebalancing Feedback and the Blind Spots of Scalar Stability Monitoring",
     "The stability of markets hosting leveraged exchange-traded products is governed not by any single product's loop gain but by the spectral radius of a loop-gain matrix, and scalar per-product monitoring underestimates system feedback by construction. Recent work measures the self-reinforcement of a leveraged fund's daily close rebalancing through a scalar loop gain and treats cross-asset spillovers as bias. We model complexes on correlated underlyings as a coupled feedback system with matrix gain L and show that scalar monitoring has two blind spots: (i) cycle amplification, since rho(L) >= max"),
    # arxiv:2608.21888
    ("arxiv:2608.21888", "Short-horizon mean reversion in cryptocurrency markets: a matched cross-market measurement",
     "At 15-minute horizons, directional mean reversion is far stronger and more pervasive in cryptocurrency markets than in US equities: scored under one matched, strictly out-of-sample protocol, 90% of 183 Binance pairs carry significant directional reversal against 2.7% of 187 US stocks and ETFs, in every focal coin-year since 2021. The signal lives in signs, not magnitudes: lag-one return autocorrelation is near zero on the major coins, yet simply betting against the previous candle captures most of the effect. US-listed funds whose net asset value is a crypto or metal price inherit their underl"),
    # arxiv:2608.18195
    ("arxiv:2608.18195", "Multi-Level Market Making with Reinforcement Learning",
     "We introduce a reinforcement learning framework for market making in a limit order book. Our algorithm aims to maximize trading revenue by dynamically submitting market and limit orders of varying sizes across multiple price levels while controlling inventory size. We use multivariate logistic-normal distributions to model order allocations and employ a deep-set encoder to aggregate features from variable-length order sets into a fixed-dimensional latent representation. Additionally, we incorporate potential-based reward shaping to accelerate learning without altering the optimal policy. We il"),
    # arxiv:2608.13096
    ("arxiv:2608.13096", "FlowLOB: Efficient and Controllable Limit Order Book Generation with Flow Matching",
     "Limit order book (LOB) simulators are most useful to practitioners when they combine realistic market dynamics, computationally efficient sampling, controllable scenario generation, and the ability to generalize beyond the instruments seen during training---properties that existing agent-based and deep generative simulators provide only partially. We present \\textbf{FlowLOB}, a conditional \\textbf{flow}-matching generator of \\textbf{LOB} trajectories, trained on multiple Hong Kong Exchange (HKEX) symbols at three sampling frequencies ($0.1$s, $1$s, $10$s) in tick-relative representation that t"),
]

_MEAN_REVERSION_ID = "arxiv:2608.21888"


def _cand(id_, titulo, abstract):
    return {"titulo": titulo, "abstract": abstract}


def test_run001_10_no_estrategias_mueren_y_mean_reversion_sobrevive():
    survive, kill = [], []
    for id_, titulo, abstract in RUN001_SURVIVORS:
        ok, _ = estimate.is_operable_strategy(_cand(id_, titulo, abstract))
        (survive if ok else kill).append(id_)
    # exactamente 1 sobrevive (mean reversion), 10 mueren
    assert survive == [_MEAN_REVERSION_ID], f"sobreviven={survive}"
    assert len(kill) == 10


def test_positive_controls_survive():
    # estrategias reales conocidas deben pasar el eje (sin falsos negativos groseros)
    for ab in [
        "A time series momentum strategy: we go long assets with positive past returns and short the rest, rebalanced monthly.",
        "A carry strategy in FX: long high-yield currencies, short low-yield, earning a risk premium.",
        "The turn-of-the-month seasonal anomaly: buy the index on the last day and hold three days.",
    ]:
        ok, _ = estimate.is_operable_strategy({"titulo": "", "abstract": ab})
        assert ok


def test_method_paper_killed():
    ok, _ = estimate.is_operable_strategy({"titulo": "A new estimator",
        "abstract": "We propose a test for conditional mean independence and prove its convergence."})
    assert not ok


def test_prediction_alone_is_not_a_strategy():
    # lección H003/OFI: predecir ≠ negociar. "predict"/"signal" a secas NO bastan.
    ok, _ = estimate.is_operable_strategy({"titulo": "AI-driven interest rate forecasting",
        "abstract": "We build a model that predicts rates; a strong predictive signal out-of-sample."})
    assert not ok
    # pero una FAMILIA de estrategia nombrada o un verbo de ejecución sí
    ok2, _ = estimate.is_operable_strategy({"titulo": "", "abstract": "a momentum strategy: we go long winners"})
    assert ok2


# ===== Refinamiento run 002: los 4 falsos positivos deben morir, el sectorial sobrevive =====
RUN002_SURVIVORS = [
    ("arxiv:2608.10788", "The Triadic Stress Index in Financial Markets",
     "The Triadic Stress Index (TSI) takes a network index whose four factors were first observed in soil microbiome co-occurrence networks and applies it, without alteration, to the correlation network of financial assets. We test it on five markets spanning 2006-2026 (equities including banking crises and the AI sector, cryptocurrencies, commodities, foreign exchange and sovereign debt), against three independent definitions of a crisis episode, at a fixed alarm budget, out of sample, with block-bootstrap intervals and a Holm correction across the family of tests. The benchmarks are the Absorption Ratio, the industry standard used by MSCI and central banks; the effective rank and the Vendi score"),
    ("quantpedia:https-quantpedia-com-sectoral-intramonth-momentum-cycle", "Sectoral Intramonth Momentum Cycle: Exploiting Turn-of-the-Month Patterns in Sector ETF Strategies",
     "We document a persistent intramonth momentum cycle in U.S. sector ETFs that yields meaningful risk-adjusted returns when properly sequenced. Using the nine original Select Sector SPDR ETFs and SPY as the market benchmark from December 1998 through June 2026, we show that trailing 252-day sector momentum generates a positive spread on the first trading day of the month\u2014and then sharply reverses on days two and three. A third, independent leg of the cycle emerges in the window from ten to five trading days before month-end, consistent with the intramonth momentum cycle recently documented at the single-stock level by Nathan, Suominen and Tasa (2026). Stitching the three legs togethe"),
    ("quantpedia:https-quantpedia-com-from-backtest-to-benchmark-validating-n", "From Backtest to Benchmark: Validating New Strategies with Quantpedia API",
     "A profitable backtest is rarely the end of a research process. In professional quantitative research, the more important question often comes after the first positive result: is the strategy genuinely new, or is it simply another version of an already known factor, timing rule, or anomaly? This is especially relevant when a researcher develops a new systematic strategy with a clean historical equity curve. The strategy may have acceptable risk-adjusted performance, stable drawdowns, and a logical trading rule, but those statistics alone do not prove that the idea is unique. A silver strategy, for example, may look different on the surface while still behaving like a known commodit"),
    ("arxiv:2608.07709", "Microstructural Foundation for the Rough Hawkes--Heston Model",
     "Hawkes-based microstructural foundations for rough volatility, leverage, and rough Heston-type limits were developed by El Euch et al. (2018, Finance Stoch., 22(2), 241--280) and connected to the affine rough Heston framework of El Euch and Rosenbaum (2019, Math. Finance, 29(1), 3--38). The rough Hawkes--Heston model with common price--volatility jumps of Bondi et al. (2024, Math. Finance, 34(4), 1197--1241) extends this framework by adding state-dependent common jumps to rough affine volatility. We provide a microstructural foundation for its variance and common-jump mechanism by constructing a Poisson-embedded marked Hawkes order-flow model. Ordinary arrivals generate rough continuous vola"),
    ("arxiv:2608.04373", "Public Trader Identity: Adverse Selection and Return Predictability",
     "Informed traders are supposed to need anonymity: they profit by hiding among the uninformed. A decentralized exchange now publishes the counterparty. Every committed order, cancellation, rejection, and fill carries a persistent pseudonymous wallet address. We reconstruct the full-depth limit order book from a record of 17.1 billion messages and 14.3 million aggressive orders by 147,113 wallets, covering $84.3 billion in taker notional. We report three findings. First, informativeness is a persistent wallet attribute. Wallets ranked by the price movement following their aggressive orders retain that ordering across adjacent ten-day windows, with a rank correlation of 0.52. Second, the ranking"),
]

_SECTORAL_ID_SUBSTR = "sectoral"


def test_run002_4_falsos_positivos_mueren_sectorial_sobrevive():
    survive, kill = [], []
    for id_, titulo, abstract in RUN002_SURVIVORS:
        ok, _ = estimate.is_operable_strategy({"titulo": titulo, "abstract": abstract})
        (survive if ok else kill).append(id_)
    # sólo el candidato sectorial (estrategia real) sobrevive; los 4 falsos positivos mueren
    assert len(survive) == 1 and _SECTORAL_ID_SUBSTR in survive[0], f"survive={survive}"
    assert len(kill) == 4


def test_inoperable_horizon_rejected():
    ok, why = estimate.is_operable_strategy({"titulo": "return predictability",
        "abstract": "we predict one-second returns and go long the top wallets"})
    assert not ok and "horizonte" in why


def test_word_boundary_no_false_positive_carry():
    # "carrying" NO debe disparar 'carry'; sin otra señal → no es estrategia
    ok, _ = estimate.is_operable_strategy({"titulo": "A stress index",
        "abstract": "the index, carrying a per-node decomposition, names the asset along the network"})
    assert not ok
