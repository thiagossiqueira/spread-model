# tests/test_interpolation.py
import numpy as np
import pandas as pd
from src.utils.interpolation import interpolate_di_surface, interpolate_yield_for_tenor

def test_interpolate_di_surface_linear():
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
    assert np.isclose(result.iloc[0]["2.5-year"], 11.5)

def test_interpolate_yield_for_tenor():
    index = pd.to_datetime(["2024-01-01"])
    yc_table = pd.DataFrame({"1-year": [10.0], "2-year": [11.0], "3-year": [12.0]}, index=index)
    tenors = {"1-year": 1.0, "2-year": 2.0, "3-year": 3.0}

    interpolated = interpolate_yield_for_tenor(index[0], yc_table, 2.5, tenors)
    assert np.isclose(interpolated, 11.5)
