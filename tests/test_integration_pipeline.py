# tests/test_integration_pipeline.py

import pandas as pd
from utils.file_io import load_inputs
from utils.interpolation import interpolate_di_surface
from config import CONFIG

def test_load_and_interpolate_produces_some_valid_curves():
    surface, _, _ = load_inputs(CONFIG)

    valid_surface = (
        surface.groupby("curve_id")
        .filter(lambda df: df["tenor"].nunique() >= 2)
    )

    assert not valid_surface.empty, "Nenhuma curva válida com 2+ tenores foi encontrada!"
