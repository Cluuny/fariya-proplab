"""Tests del loader del corpus de papers (parseo de manifiesto + resolución visible)."""

from __future__ import annotations

import pytest

from src.pipeline import papers

_MANIFEST = """# MANIFEST

## foo2020_bar.pdf
- título: Foo
- autores: Baz
- SHA256: abc123
- usado en: HX
- estado: presente

## missing2019_qux.pdf
- título: Missing
- SHA256: —
- estado: pendiente
"""


@pytest.fixture
def corpus(tmp_path):
    man = tmp_path / "MANIFEST.md"
    man.write_text(_MANIFEST)
    (tmp_path / "foo2020_bar.pdf").write_bytes(b"%PDF-1.4 fake")
    return tmp_path, man


def test_parse_manifest(corpus):
    _dir, man = corpus
    e = papers.parse_manifest(man)
    assert set(e) == {"foo2020_bar", "missing2019_qux"}
    assert e["foo2020_bar"]["sha256"] == "abc123"
    assert e["missing2019_qux"]["sha256"] is None      # "—" → None
    assert e["missing2019_qux"]["estado"] == "pendiente"


def test_resolve_present(corpus):
    d, man = corpus
    p = papers.resolve_paper("foo2020_bar", papers_dir=d, manifest=man)
    assert p.name == "foo2020_bar.pdf" and p.exists()
    # acepta el id con o sin .pdf
    assert papers.resolve_paper("foo2020_bar.pdf", papers_dir=d, manifest=man) == p


def test_resolve_missing_file_fails_visibly(corpus):
    d, man = corpus
    with pytest.raises(papers.PaperNotFoundError) as ei:
        papers.resolve_paper("missing2019_qux", papers_dir=d, manifest=man)
    assert "pendiente" in str(ei.value)


def test_resolve_unknown_id_fails_visibly(corpus):
    d, man = corpus
    with pytest.raises(papers.PaperNotFoundError) as ei:
        papers.resolve_paper("nope", papers_dir=d, manifest=man)
    assert "no está en el manifiesto" in str(ei.value)


def test_no_obtenible_is_a_valid_state(tmp_path):
    man = tmp_path / "MANIFEST.md"
    man.write_text("## gone1987_x.pdf\n- título: Gone\n- SHA256: —\n- estado: no_obtenible\n")
    e = papers.parse_manifest(man)
    assert e["gone1987_x"]["estado"] == "no_obtenible"   # distinto de 'pendiente'


def test_real_manifest_ariel_no_obtenible():
    e = papers.parse_manifest()
    assert e["ariel1987_tom"]["estado"] == "no_obtenible"
    assert "hurst2017_trend" in e   # sustituto del test ciego catalogado


def test_real_manifest_parses_and_is_consistent():
    """El manifiesto real del repo parsea y sus entradas presentes cuadran en SHA256
    (si los PDFs están; si no, se omite — son gitignored)."""
    e = papers.parse_manifest()
    assert "contkukanov2011_ofi" in e and "moskowitz2012_tsmom" in e
    for pid, meta in e.items():
        path = papers.PAPERS_DIR / meta["filename"]
        if path.exists() and meta.get("sha256"):
            assert papers.sha256_file(path) == meta["sha256"], f"SHA256 no cuadra: {pid}"
