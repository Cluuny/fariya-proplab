"""Section 5 — reporting: minimum metrics present and deterministic report."""

import numpy as np
import pandas as pd

from src import report


def _returns(n=300, seed=3):
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2020-01-01", periods=n)
    return pd.Series(rng.normal(0.0003, 0.01, n), index=dates, name="return")


def test_report_contains_minimum_metrics():
    md = report.render(_returns(), name="test")
    for token in ("Sharpe", "Max drawdown", "Equity curve", "Distribución de retornos"):
        assert token in md


def test_metrics_values_are_sane():
    r = _returns()
    m = report.metrics(r)
    assert m["n_obs"] == len(r)
    assert -1.0 <= m["max_drawdown"] <= 0.0
    assert m["final_equity"] > 0


def test_report_is_deterministic():
    r = _returns()
    assert report.render(r, name="x") == report.render(r, name="x")


def test_generate_writes_file(tmp_path):
    r = _returns()
    path = report.generate(r, name="bh", out_dir=tmp_path)
    assert path.exists()
    assert path.read_text(encoding="utf-8") == report.render(r, name="bh")


def test_equity_curve_and_drawdown():
    # Series with a known drawdown: +10% then -50%.
    r = pd.Series([0.10, -0.50], index=pd.bdate_range("2020-01-01", periods=2))
    eq = report.equity_curve(r)
    assert np.isclose(eq.iloc[-1], 1.10 * 0.50)
    # From the peak (1.10) it falls to 0.55 → DD = 0.55/1.10 - 1 = -0.5.
    assert np.isclose(report.max_drawdown(r), -0.5)
