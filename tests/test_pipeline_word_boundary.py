"""Regla: los gates de DECISIÓN por palabra clave usan LÍMITE DE PALABRA (\\b), sin excepción.

Tres bugs del mismo tipo bastaron para hacerla regla: 'ict'⊂'predict' (falsabilidad),
'carry'⊂'carrying' y 'long the'⊂'along the' (es_estrategia_operable). Este test genérico pasa una
batería de palabras-trampa (una palabra corta del gate embebida dentro de otra) por los gates de
decisión y verifica que NINGUNA dispara un falso positivo.
"""

from __future__ import annotations

from src.pipeline import estimate, triage_operability

# palabra-trampa → (contiene como subcadena) un término de algún gate, pero NO es ese término
_TRAP_SENTENCES = [
    "we predict returns with an explicit and implicit model",   # predict/explicit/implicit ⊃ 'ict'
    "the index, carrying the concentration along the network",   # carrying ⊃ 'carry'; along ⊃ 'long the'
    "a restrictive verdict on the conflicting signals",          # restrictive/verdict/conflicting ⊃ 'ict'
    "monetary policy and momentum are distinct",                 # control words near real terms
    "seasonality of the seasoned equity offerings",              # 'season' vs 'seasonal'
]


def test_falsifiability_gate_no_substring_false_positive():
    # ninguna trampa debe ser rechazada por FALSABILIDAD (los acrónimos ICT/SMC/FVG con \\b)
    for s in _TRAP_SENTENCES:
        v = triage_operability.triage_operability({"titulo": "", "abstract": s})
        assert v.categoria != "falsabilidad", f"falso positivo de falsabilidad en: {s!r}"


def test_strategy_axis_no_substring_false_positive():
    # 'carrying'/'along the' NO deben contar como 'carry'/'long the' → sin regla, no es estrategia
    for s in ["the index, carrying a decomposition along the network of assets",
              "we forecast and predict the explicit latent state"]:
        ok, _ = estimate.is_operable_strategy({"titulo": "", "abstract": s})
        assert not ok, f"falso positivo de estrategia en: {s!r}"


def test_word_boundary_helpers_are_strict():
    # los helpers \\b no casan subcadenas dentro de palabras...
    assert estimate._hits_word("carrying the load", ("carry",)) is None
    assert estimate._hits_word("along the way", ("long the",)) is None
    assert triage_operability._hits_word("we predict x", ("ict",)) is None
    # ...pero SÍ casan el término como palabra
    assert estimate._hits_word("a carry strategy", ("carry",)) == "carry"
    assert triage_operability._hits_word("an ict order block", ("ict",)) == "ict"
