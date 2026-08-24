"""discover.py — Estación 1: Descubrimiento.

Fuentes con acceso programático, en orden de facilidad:
  - arXiv API (q-fin.PM, q-fin.ST, q-fin.TR) — la única con API limpia (Atom).
  - RSS de Alpha Architect.
  - RSS de CXO Advisory.
  - SSRN: sin API pública → ingesta MANUAL de URLs por ahora (`manual_candidate`).

Salida: cola de candidatos SIN procesar en la DB (título, abstract, url, fecha, fuente).

Cron: MENSUAL, no diario. El throughput real del sistema es ~una hipótesis al mes;
generar 50 fichas semanales fabrica inventario muerto. (El scheduling concreto vive en el
runner `scripts/pipeline.py discover`, invocado por un cron mensual del entorno.)

La red se toca sólo en `fetch_*`; el PARSEO (`parse_arxiv_atom`, `parse_rss`) es puro y
testeable sobre fixtures, sin salir a Internet.
"""

from __future__ import annotations

import urllib.request
import xml.etree.ElementTree as ET

ARXIV_API = "http://export.arxiv.org/api/query"
ARXIV_CATS = ("q-fin.PM", "q-fin.ST", "q-fin.TR")
RSS_FEEDS = {
    "alpha_architect": "https://alphaarchitect.com/feed/",
    "cxo": "https://www.cxoadvisory.com/feed/",
}
_ATOM_NS = {"a": "http://www.w3.org/2005/Atom"}
_USER_AGENT = "PropLab-research-pipeline/1 (monthly discovery; contact vicente@getvaas.com)"


def _http_get(url: str, timeout: float = 20.0) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


# ---------------------------------------------------------------- arXiv (Atom)
def arxiv_query_url(cats=ARXIV_CATS, *, max_results: int = 50, start: int = 0) -> str:
    query = "+OR+".join(f"cat:{c}" for c in cats)
    return (
        f"{ARXIV_API}?search_query={query}&start={start}&max_results={max_results}"
        "&sortBy=submittedDate&sortOrder=descending"
    )


def parse_arxiv_atom(xml_text: str) -> list[dict]:
    """Parse an arXiv Atom feed into candidate dicts (pure; no network)."""
    root = ET.fromstring(xml_text)
    out = []
    for e in root.findall("a:entry", _ATOM_NS):
        def _txt(tag):
            node = e.find(f"a:{tag}", _ATOM_NS)
            return (node.text or "").strip() if node is not None else ""

        url = _txt("id")
        out.append({
            "id": _arxiv_id(url),
            "titulo": " ".join(_txt("title").split()),
            "abstract": " ".join(_txt("summary").split()),
            "url": url,
            "fecha": _txt("published")[:10],
            "fuente": "arxiv",
            "fuente_de_la_idea": "pipeline",
            "estado": "candidato",
        })
    return out


def _arxiv_id(url: str) -> str:
    # http://arxiv.org/abs/2401.01234v1 -> arxiv:2401.01234
    tail = url.rstrip("/").split("/abs/")[-1]
    return "arxiv:" + tail.split("v")[0] if tail else "arxiv:unknown"


def fetch_arxiv(cats=ARXIV_CATS, *, max_results: int = 50) -> list[dict]:
    return parse_arxiv_atom(_http_get(arxiv_query_url(cats, max_results=max_results)))


# ------------------------------------------------------------------ RSS 2.0
def parse_rss(xml_text: str, source: str) -> list[dict]:
    """Parse an RSS 2.0 feed into candidate dicts (pure; no network)."""
    root = ET.fromstring(xml_text)
    channel = root.find("channel")
    items = (channel.findall("item") if channel is not None else root.findall(".//item"))
    out = []
    for it in items:
        def _txt(tag):
            node = it.find(tag)
            return (node.text or "").strip() if node is not None else ""

        link = _txt("link")
        title = " ".join(_txt("title").split())
        out.append({
            "id": f"{source}:{_slug(link or title)}",
            "titulo": title,
            "abstract": " ".join(_txt("description").split()),
            "url": link,
            "fecha": _txt("pubDate")[:16],
            "fuente": source,
            "fuente_de_la_idea": "pipeline",
            "estado": "candidato",
        })
    return out


def _slug(text: str) -> str:
    keep = "".join(c if c.isalnum() else "-" for c in text.lower())
    return "-".join(p for p in keep.split("-") if p)[:60] or "unknown"


def fetch_rss(source: str, url: str | None = None) -> list[dict]:
    url = url or RSS_FEEDS[source]
    return parse_rss(_http_get(url), source)


# ---------------------------------------------------------------- SSRN manual
def manual_candidate(url: str, titulo: str, abstract: str = "", fecha: str = "") -> dict:
    """Build a candidate from a hand-entered SSRN (or other) URL — no API available."""
    return {
        "id": f"manual:{_slug(url or titulo)}",
        "titulo": titulo,
        "abstract": abstract,
        "url": url,
        "fecha": fecha,
        "fuente": "ssrn" if "ssrn" in (url or "").lower() else "manual",
        "fuente_de_la_idea": "humano",
        "estado": "candidato",
    }


# ---------------------------------------------------------------- orchestration
def discover(conn, *, max_results: int = 50, include_rss: bool = True) -> dict:
    """Fetch all programmatic sources and upsert new candidates. Robust to per-source
    network failure: a source that raises is skipped and reported, not fatal.

    Returns a per-source count of candidates written.
    """
    from src.pipeline import db

    counts: dict[str, int] = {}
    sources: list[tuple[str, callable]] = [("arxiv", lambda: fetch_arxiv(max_results=max_results))]
    if include_rss:
        for src in RSS_FEEDS:
            sources.append((src, (lambda s=src: fetch_rss(s))))

    for name, fn in sources:
        try:
            cands = fn()
        except Exception as ex:  # noqa: BLE001 — una fuente caída no debe tumbar el resto
            counts[name] = -1  # -1 = fuente falló (se distingue de 0 = sin novedades)
            print(f"[discover] fuente '{name}' falló: {type(ex).__name__}: {ex}")
            continue
        written = 0
        for c in cands:
            if db.get(conn, c["id"]) is None:  # sólo candidatos nuevos
                db.upsert(conn, c)
                written += 1
        counts[name] = written
    return counts
