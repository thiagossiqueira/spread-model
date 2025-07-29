# tests/test_interpolation.py
import numpy as np
import pandas as pd
from utils.interpolation import interpolate_di_surface, interpolate_yield_for_tenor
from finmath.curve_models import flat_forward_interpolation

def test_interpolate_di_surface_flat_forward():
    surface = pd.DataFrame({
        "obs_date": ["2024-01-01"] * 3,
        "tenor": [1.0, 2.0, 3.0],
        "yield": [10.0, 11.0, 12.0],
        "id": ["X", "Y", "Z"]
    })
    surface["obs_date"] = pd.to_datetime(surface["obs_date"])

    tenors = {"1-year": 1.0, "2-year": 2.0, "3-year": 3.0, "2.5-year": 2.5}
    result = interpolate_di_surface(surface, tenors)

    assert not result.empty
    assert result.shape[0] == 1

    # Validar com interpolação flat-forward diretamente
    curva = pd.Series([10.0, 11.0, 12.0], index=[1.0, 2.0, 3.0])
    esperado = flat_forward_interpolation(2.5, curva)
    assert np.isclose(result.iloc[0]["2.5-year"], esperado, atol=0.0001)

def test_interpolate_yield_for_tenor_flat_forward():
    index = pd.to_datetime(["2024-01-01"])
    yc_table = pd.DataFrame({"1-year": [10.0], "2-year": [11.0], "3-year": [12.0]}, index=index)
    tenors = {"1-year": 1.0, "2-year": 2.0, "3-year": 3.0}

    curva = pd.Series([10.0, 11.0, 12.0], index=[1.0, 2.0, 3.0])
    esperado = flat_forward_interpolation(2.5, curva)

    interpolado = interpolate_yield_for_tenor(index[0], yc_table, 2.5, tenors)
    assert np.isclose(interpolado, esperado, atol=0.0001)
