"""Section 1 — verifies repo structure, config and stubs."""

import importlib

from src import config


def test_directory_structure_exists():
    assert config.DATA_RAW.is_dir()
    assert config.DATA_CLEAN.is_dir()
    assert config.RESULTS.is_dir()
    assert (config.ROOT / "hypotheses").is_dir()
    assert (config.ROOT / "notebooks").is_dir()


def test_config_universe():
    # 17: 5 majors + 6 cruces FX + 2 metales + 4 índices. BRENT/energía y US30
    # (misma exposición que SPX500) retirados. Cada activo mapeado a Dukascopy.
    assert len(config.INSTRUMENTS) == 17
    assert "US30" not in config.INSTRUMENTS
    assert "EURUSD" in config.INSTRUMENTS and "EURCHF" in config.INSTRUMENTS
    assert all(sym in config.DUKASCOPY_SYMBOLS for sym in config.INSTRUMENTS)
    assert config.ANOMALOUS_RETURN_SIGMA == 5.0


def test_cost_model_per_instrument():
    for sym in config.INSTRUMENTS:
        assert sym in config.COSTS


def test_modules_importable():
    for name in ("loaders", "signals", "engine", "report", "challenge"):
        importlib.import_module(f"src.{name}")


def test_challenge_module_exposes_simulator():
    # challenge.py is now implemented (Block B); it used to be a stub.
    from src import challenge

    assert callable(challenge.simulate_challenge)
    assert callable(challenge.analytic_pass_probability)
