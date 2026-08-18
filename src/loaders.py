"""loaders.py — Data layer: raw -> clean + quality validation.

Converts raw dumps (`data/raw/`, IMMUTABLE) into clean parquet
(`data/clean/`, one per instrument) and produces a readable quality report.

Hard rules (master document):
- `data/raw/` is never modified; every clean output is derived and regenerable.
- One parquet file per instrument, indexed by ascending date, with no
  duplicate dates.

Default expected raw format: CSV with a date column and price columns (OHLC or
at least close). The concrete Dukascopy parsing is tuned once the first real
dump is inspected (design.md — Open Questions); the public contract of this
module does not change because of it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from src import config

# Candidate price columns, in order of preference for "close".
_CLOSE_CANDIDATES = ("close", "Close", "CLOSE", "adj_close", "Adj Close")
_PRICE_COLUMNS = ("open", "high", "low", "close")


@dataclass
class Anomaly:
    """A detected anomaly: instrument, date and kind."""

    instrument: str
    date: pd.Timestamp | None
    kind: str
    detail: str = ""


@dataclass
class QualityReport:
    """Quality report for an instrument."""

    instrument: str
    n_obs: int
    start: pd.Timestamp | None
    end: pd.Timestamp | None
    missing_days: int
    anomalies: list[Anomaly] = field(default_factory=list)

    def counts_by_kind(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for a in self.anomalies:
            out[a.kind] = out.get(a.kind, 0) + 1
        return out


# --------------------------------------------------------------------------- #
# Reading raw files (without mutating them)                                   #
# --------------------------------------------------------------------------- #
def read_raw(path: Path) -> pd.DataFrame:
    """Read a raw file into a date-indexed DataFrame, without modifying the file.

    Accepts CSV with a date column (first column named like
    date/time/timestamp, or just the first column) and price columns.
    """
    df = pd.read_csv(path)
    # Detect the date column.
    date_col = None
    for c in df.columns:
        if str(c).lower() in ("date", "time", "timestamp", "datetime", "gmt time"):
            date_col = c
            break
    if date_col is None:
        date_col = df.columns[0]
    idx = pd.to_datetime(df[date_col], errors="coerce", utc=False)
    df = df.drop(columns=[date_col])
    df.index = pd.DatetimeIndex(idx.dt.normalize() if hasattr(idx, "dt") else idx, name="date")
    # Normalize price column names to known lowercase forms.
    rename = {}
    for c in df.columns:
        lc = str(c).lower()
        if lc in _PRICE_COLUMNS:
            rename[c] = lc
        elif c in _CLOSE_CANDIDATES:
            rename[c] = "close"
    df = df.rename(columns=rename)
    return df


def _close_series(df: pd.DataFrame) -> pd.Series:
    for name in ("close", *_CLOSE_CANDIDATES):
        if name in df.columns:
            return pd.to_numeric(df[name], errors="coerce")
    # Fallback: first numeric column.
    num = df.select_dtypes(include="number")
    if num.shape[1] == 0:
        raise ValueError("No se encontró columna de precio numérica")
    return num.iloc[:, 0]


# --------------------------------------------------------------------------- #
# Cleaning                                                                    #
# --------------------------------------------------------------------------- #
def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Sort by date, drop duplicate dates (keep the last one).

    Does not invent data: it only sorts and deduplicates. Anomaly detection is
    the responsibility of `validate`.
    """
    out = df.sort_index()
    out = out[~out.index.duplicated(keep="last")]
    return out


# --------------------------------------------------------------------------- #
# Quality validation                                                          #
# --------------------------------------------------------------------------- #
def _detect_contract_jumps(returns: pd.Series, sigma: float) -> pd.Index:
    """Abrupt jumps that may indicate a contract change: return > `sigma`·σ.

    Reported as flags for human review, not corrected.
    """
    if returns.std(ddof=0) == 0 or returns.dropna().empty:
        return returns.index[:0]
    z = (returns - returns.mean()) / returns.std(ddof=0)
    return returns.index[z.abs() > sigma]


def validate(
    instrument: str,
    df: pd.DataFrame,
    *,
    raw_had_duplicates: bool = False,
    sigma: float = config.ANOMALOUS_RETURN_SIGMA,
) -> QualityReport:
    """Validate an already-sorted series and detect anomalies.

    Detects: calendar gaps (missing business days), zero/non-positive prices,
    duplicate dates (in the raw file), anomalous returns > `sigma`·σ, and
    abrupt jumps from a possible contract change.
    """
    anomalies: list[Anomaly] = []
    close = _close_series(df)

    # Zero or non-positive prices.
    nonpos = close[(close <= 0) | close.isna()]
    for ts in nonpos.index:
        anomalies.append(Anomaly(instrument, ts, "nonpositive_price"))

    # Duplicate dates (detected before deduplicating).
    if raw_had_duplicates:
        anomalies.append(Anomaly(instrument, None, "duplicate_dates"))

    # Returns.
    returns = np.log(close.where(close > 0)).diff()

    # Anomalous returns (>sigma·σ).
    std = returns.std(ddof=0)
    if std and not np.isnan(std) and std > 0:
        mean = returns.mean()
        z = (returns - mean) / std
        for ts in returns.index[z.abs() > sigma]:
            anomalies.append(
                Anomaly(instrument, ts, "anomalous_return", f"z={z.loc[ts]:.1f}")
            )

    # Contract-change jumps (flag for human review).
    for ts in _detect_contract_jumps(returns, sigma):
        anomalies.append(Anomaly(instrument, ts, "contract_jump"))

    # Calendar gaps: business days (Mon-Fri) with no observation.
    missing = 0
    if len(df.index) >= 2:
        bdays = pd.bdate_range(df.index.min(), df.index.max())
        missing = int(len(bdays.difference(df.index)))
        if missing:
            anomalies.append(
                Anomaly(instrument, None, "calendar_gap", f"{missing} días hábiles")
            )

    return QualityReport(
        instrument=instrument,
        n_obs=int(len(df.index)),
        start=df.index.min() if len(df.index) else None,
        end=df.index.max() if len(df.index) else None,
        missing_days=missing,
        anomalies=anomalies,
    )


# --------------------------------------------------------------------------- #
# raw -> clean orchestration                                                  #
# --------------------------------------------------------------------------- #
def _instrument_from_path(path: Path) -> str:
    return path.stem.upper()


def process_file(
    raw_path: Path, clean_dir: Path = config.DATA_CLEAN
) -> tuple[Path, QualityReport]:
    """Process one raw file -> clean parquet + report, without touching the raw file."""
    instrument = _instrument_from_path(raw_path)
    raw = read_raw(raw_path)
    had_dupes = bool(raw.index.duplicated().any())
    cleaned = clean(raw)
    report = validate(instrument, cleaned, raw_had_duplicates=had_dupes)
    clean_dir.mkdir(parents=True, exist_ok=True)
    out_path = clean_dir / f"{instrument}.parquet"
    cleaned.to_parquet(out_path)
    return out_path, report


def render_report(reports: list[QualityReport]) -> str:
    """Readable quality report (markdown), per instrument."""
    lines = ["# Reporte de calidad de datos", ""]
    lines.append("| Instrumento | Obs | Desde | Hasta | Días faltantes | Anomalías |")
    lines.append("|---|---|---|---|---|---|")
    for r in reports:
        kinds = r.counts_by_kind()
        summary = ", ".join(f"{k}={v}" for k, v in sorted(kinds.items())) or "—"
        start = r.start.date() if r.start is not None else "—"
        end = r.end.date() if r.end is not None else "—"
        lines.append(
            f"| {r.instrument} | {r.n_obs} | {start} | {end} | {r.missing_days} | {summary} |"
        )
    lines.append("")
    for r in reports:
        detail = [a for a in r.anomalies if a.date is not None]
        if detail:
            lines.append(f"## {r.instrument} — anomalías con fecha")
            for a in detail[:200]:
                lines.append(f"- {a.date.date()} · {a.kind} {a.detail}".rstrip())
            if len(detail) > 200:
                lines.append(f"- … (+{len(detail) - 200} más)")
            lines.append("")
    return "\n".join(lines)


def run(
    raw_dir: Path = config.DATA_RAW, clean_dir: Path = config.DATA_CLEAN
) -> list[QualityReport]:
    """Process all raw files and write the quality report."""
    raw_files = sorted(
        p for p in raw_dir.glob("*") if p.suffix.lower() in (".csv", ".txt")
    )
    reports: list[QualityReport] = []
    for path in raw_files:
        _, report = process_file(path, clean_dir)
        reports.append(report)
    report_md = render_report(reports)
    clean_dir.mkdir(parents=True, exist_ok=True)
    (clean_dir.parent / "quality_report.md").write_text(report_md, encoding="utf-8")
    return reports


def main() -> int:
    reports = run()
    if not reports:
        print(
            f"No se encontraron crudos en {config.DATA_RAW}. "
            "Coloca los dumps de Dukascopy (CSV) antes de correr."
        )
        return 0
    print(render_report(reports))
    print(f"\n{len(reports)} instrumentos procesados -> {config.DATA_CLEAN}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
