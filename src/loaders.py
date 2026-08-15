"""loaders.py — Capa de datos: raw -> clean + validación de calidad.

Convierte dumps crudos (`data/raw/`, INMUTABLE) en parquet limpio
(`data/clean/`, uno por instrumento) y produce un reporte de calidad legible.

Reglas duras (documento maestro):
- `data/raw/` nunca se modifica; toda salida limpia es derivada y regenerable.
- Un archivo parquet por instrumento, indexado por fecha ascendente, sin
  fechas duplicadas.

Formato de crudo esperado por defecto: CSV con una columna de fecha y columnas
de precio (OHLC o al menos cierre). El parseo concreto de Dukascopy se ajusta
al inspeccionar el primer dump real (design.md — Open Questions); el contrato
público de este módulo no cambia por ello.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from src import config

# Columnas de precio candidatas, en orden de preferencia para "cierre".
_CLOSE_CANDIDATES = ("close", "Close", "CLOSE", "adj_close", "Adj Close")
_PRICE_COLUMNS = ("open", "high", "low", "close")


@dataclass
class Anomaly:
    """Una anomalía detectada: instrumento, fecha y tipo."""

    instrument: str
    date: pd.Timestamp | None
    kind: str
    detail: str = ""


@dataclass
class QualityReport:
    """Reporte de calidad de un instrumento."""

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
# Lectura de crudos (sin mutarlos)                                            #
# --------------------------------------------------------------------------- #
def read_raw(path: Path) -> pd.DataFrame:
    """Lee un archivo crudo a DataFrame indexado por fecha, sin modificar el archivo.

    Acepta CSV con una columna de fecha (primera columna con nombre tipo
    date/time/timestamp o la primera columna a secas) y columnas de precio.
    """
    df = pd.read_csv(path)
    # Detectar columna de fecha.
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
    # Normalizar nombres de columnas de precio a minúsculas conocidas.
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
    # Fallback: primera columna numérica.
    num = df.select_dtypes(include="number")
    if num.shape[1] == 0:
        raise ValueError("No se encontró columna de precio numérica")
    return num.iloc[:, 0]


# --------------------------------------------------------------------------- #
# Limpieza                                                                    #
# --------------------------------------------------------------------------- #
def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Ordena por fecha, elimina duplicados de fecha (conserva el último).

    No inventa datos: sólo ordena y deduplica. La detección de anomalías es
    responsabilidad de `validate`.
    """
    out = df.sort_index()
    out = out[~out.index.duplicated(keep="last")]
    return out


# --------------------------------------------------------------------------- #
# Validación de calidad                                                       #
# --------------------------------------------------------------------------- #
def _detect_contract_jumps(returns: pd.Series, sigma: float) -> pd.Index:
    """Saltos abruptos candidatos a cambio de contrato: retorno > `sigma`·σ.

    Se reporta como banderas para revisión humana, no se corrige.
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
    """Valida una serie ya ordenada y detecta anomalías.

    Detecta: gaps de calendario (días hábiles faltantes), precios en cero/no
    positivos, fechas duplicadas (en el crudo), retornos anómalos > `sigma`·σ,
    y saltos abruptos por posible cambio de contrato.
    """
    anomalies: list[Anomaly] = []
    close = _close_series(df)

    # Precios en cero o no positivos.
    nonpos = close[(close <= 0) | close.isna()]
    for ts in nonpos.index:
        anomalies.append(Anomaly(instrument, ts, "nonpositive_price"))

    # Fechas duplicadas (detectadas antes de deduplicar).
    if raw_had_duplicates:
        anomalies.append(Anomaly(instrument, None, "duplicate_dates"))

    # Retornos.
    returns = np.log(close.where(close > 0)).diff()

    # Retornos anómalos (>sigma·σ).
    std = returns.std(ddof=0)
    if std and not np.isnan(std) and std > 0:
        mean = returns.mean()
        z = (returns - mean) / std
        for ts in returns.index[z.abs() > sigma]:
            anomalies.append(
                Anomaly(instrument, ts, "anomalous_return", f"z={z.loc[ts]:.1f}")
            )

    # Saltos por cambio de contrato (bandera para revisión humana).
    for ts in _detect_contract_jumps(returns, sigma):
        anomalies.append(Anomaly(instrument, ts, "contract_jump"))

    # Gaps de calendario: días hábiles (Mon-Fri) sin observación.
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
# Orquestación raw -> clean                                                   #
# --------------------------------------------------------------------------- #
def _instrument_from_path(path: Path) -> str:
    return path.stem.upper()


def process_file(
    raw_path: Path, clean_dir: Path = config.DATA_CLEAN
) -> tuple[Path, QualityReport]:
    """Procesa un crudo -> parquet limpio + reporte, sin tocar el crudo."""
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
    """Reporte de calidad legible (markdown) por instrumento."""
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
    """Procesa todos los crudos y escribe el reporte de calidad."""
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
