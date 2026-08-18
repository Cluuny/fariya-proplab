"""Generate the avance-report KPIs FROM THE REPO — not typed by hand.

The progress report (~/Downloads/proplab_reporte_avance.html) is the only
hand-maintained artifact, so its KPIs drift (README hard rule: "todo reporte es
regenerable con un comando"). Run this and copy the numbers into the report:

    uv run python scripts/report_kpis.py
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _run(cmd: list[str]) -> str:
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True).stdout


def test_count() -> int:
    out = _run(["uv", "run", "pytest", "--collect-only", "-q"])
    # last non-empty line like "N tests collected" or count "::" lines
    return sum(1 for ln in out.splitlines() if "::" in ln)


def merged_prs() -> int:
    out = _run(["gh", "pr", "list", "--repo", "Cluuny/fariya-proplab",
                "--state", "merged", "--limit", "200", "--json", "number"])
    try:
        return len(json.loads(out or "[]"))
    except json.JSONDecodeError:
        return 0


def main() -> None:
    from src import config

    specs = sorted(p.parent.name for p in (ROOT / "openspec/specs").glob("*/spec.md"))
    archived = sorted(p.name for p in (ROOT / "openspec/changes/archive").glob("*"))
    active = [p.name for p in (ROOT / "openspec/changes").glob("*") if p.name != "archive"]
    parquets = sorted(p.stem for p in (ROOT / "data/clean").glob("*.parquet"))

    kpis = {
        "tests": test_count(),
        "prs_merged": merged_prs(),
        "instruments_active": len(config.INSTRUMENTS),
        "instruments_with_data": len(parquets),
        "specs": len(specs),
        "changes_archived": len(archived),
        "changes_active": len(active),
        "holdout_start": str(config.HOLDOUT_START),
        "sharpe_reference": f"{config.SHARPE_REFERENCE.value} ± {config.SHARPE_REFERENCE.tolerance}",
    }
    print(json.dumps(kpis, indent=2, ensure_ascii=False))
    print("\nInstrumentos activos:", ", ".join(config.INSTRUMENTS))
    print("Specs:", ", ".join(specs))


if __name__ == "__main__":
    main()
