"""test_cot.py — COT ingestion, point-in-time alignment (Bloque 2)."""
import pandas as pd
import pytest
from src import cot, config

_HAS = (config.ROOT / "data" / "cot" / "EURUSD.csv").exists()
pytestmark = pytest.mark.skipif(not _HAS, reason="data/cot/*.csv ausente (descargar de CFTC)")


def test_unmapped_fails_visibly():
    with pytest.raises(cot.CotNotMappedError):
        cot.load_cot("HK50")   # no tiene futuro US → sin mapeo


def test_indexed_by_publication_not_data_date():
    df = cot.load_cot("EURUSD")
    # el índice (publicación) es 3 días después de la fecha de datos (martes→viernes)
    assert (df.index - pd.to_datetime(df["date"])).map(lambda d: d.days).eq(3).all()


def test_point_in_time_no_lookahead():
    # Un reporte con fecha de datos el martes NO debe estar disponible hasta el
    # viernes (publicación). Comprobado con asof sobre un índice diario.
    df = cot.load_cot("EURUSD")
    # tomar un reporte concreto y su fecha de datos (martes)
    pub = df.index[500]
    data_date = pd.Timestamp(df["date"].iloc[500])
    idx = pd.bdate_range(data_date - pd.Timedelta(days=7), pub + pd.Timedelta(days=7))
    aligned = cot.align_to_prices("EURUSD", idx)
    prev_val = df["net_spec"].iloc[499]
    new_val = df["net_spec"].iloc[500]
    # el miércoles/jueves (entre datos y publicación) sigue el reporte ANTERIOR
    mid = data_date + pd.Timedelta(days=1)
    while mid.weekday() >= 5: mid += pd.Timedelta(days=1)
    if mid < pub:
        assert abs(aligned.asof(mid) - prev_val) < 1e-12  # aún no publicado
    # desde la publicación (viernes) sí aparece el nuevo
    assert abs(aligned.asof(pub) - new_val) < 1e-12
