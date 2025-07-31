# tests/test_interpolation.py

import numpy as np
import pandas as pd
from utils.interpolation import interpolate_di_surface, interpolate_yield_for_tenor
from finmath.termstructure.curve_models import flat_forward_interpolation
from calendars.daycounts import DayCounts

dc = DayCounts("bus/252", calendar="cdr_anbima")

def test_interpolate_di_surface_flat_forward():
    ref_date = pd.Timestamp("2024-01-01")
    surface = pd.DataFrame({
        "obs_date": [ref_date] * 3,
        "tenor": [
            dc.tf(ref_date, pd.Timestamp("2025-01-01")),
            dc.tf(ref_date, pd.Timestamp("2026-01-01")),
            dc.tf(ref_date, pd.Timestamp("2027-01-01")),
        ],
        "yield": [10.0, 11.0, 12.0],
        "generic_ticker_id": ["X", "Y", "Z"]
    })

    tenors = {"1-year": 1.0, "2-year": 2.0, "3-year": 3.0, "2.5-year": 2.5}
    result = interpolate_di_surface(surface, tenors)

    assert not result.empty
    assert result["curve_id"].is_unique  # verifica unicidade do identificador

    curva = pd.Series([10.0, 11.0, 12.0], index=[1.0, 2.0, 3.0])
    esperado = flat_forward_interpolation(2.5, curva)

    for val in result["2.5-year"]:
        assert np.isclose(val, esperado, atol=1e-3)


def test_interpolate_yield_for_tenor_flat_forward():
    index = pd.to_datetime(["2024-01-01"])
    tenors = {"1-year": 1.0, "2-year": 2.0, "3-year": 3.0}

    curva = pd.Series([10.0, 11.0, 12.0], index=[1.0, 2.0, 3.0])
    esperado = flat_forward_interpolation(2.5, curva)

    yc_table = pd.DataFrame({
        "1-year": [10.0],
        "2-year": [11.0],
        "3-year": [12.0],
        "obs_date": [index[0]]
    }, index=["curve1"])

    interpolado = interpolate_yield_for_tenor(index[0], yc_table, 2.5, tenors, "curve1")

    assert np.isclose(interpolado, esperado, atol=1e-3)