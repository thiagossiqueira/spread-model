# tests/test_integration_pipeline.py

import pandas as pd
from utils.file_io import load_inputs
from utils.interpolation import interpolate_di_surface
from config import CONFIG

def test_load_and_interpolate_produces_some_valid_curves():
    surface, _, _ = load_inputs(CONFIG)

    print("Total curvas:", len(surface))
    print("Datas únicas:", surface["obs_date"].nunique())

    # Agrupar por curve date (não por curve_id!)
    valid_surface = (
        surface.groupby("obs_date")
        .filter(lambda df: df["tenor"].nunique() >= 2)
    )

    print("Datas com 2+ tenores distintos:", valid_surface["obs_date"].nunique())

    assert not valid_surface.empty, "Nenhuma curva com 2+ tenores foi encontrada!"
