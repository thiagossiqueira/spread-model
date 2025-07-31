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
        "id": ["X", "Y", "Z"]
    })

    tenors = {"1-year": 1.0, "2-year": 2.0, "3-year": 3.0, "2.5-year": 2.5}
    result = interpolate_di_surface(surface, tenors)

    assert not result.empty
    assert result.shape[0] == 1

    curva = pd.Series([10.0, 11.0, 12.0], index=[1.0, 2.0, 3.0])
    esperado = flat_forward_interpolation(2.5, curva)

    assert np.isclose(result.iloc[0]["2.5-year"], esperado, atol=1e-3)

def test_interpolate_yield_for_tenor_flat_forward():
    index = pd.to_datetime(["2024-01-01"])
    yc_table = pd.DataFrame({"1-year": [10.0], "2-year": [11.0], "3-year": [12.0]}, index=index)
    tenors = {"1-year": 1.0, "2-year": 2.0, "3-year": 3.0}

    curva = pd.Series([10.0, 11.0, 12.0], index=[1.0, 2.0, 3.0])
    esperado = flat_forward_interpolation(2.5, curva)

    interpolado = interpolate_yield_for_tenor(index[0], yc_table, 2.5, tenors)
    assert np.isclose(interpolado, esperado, atol=1e-3)
