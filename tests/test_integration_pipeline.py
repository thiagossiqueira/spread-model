# tests/test_integration_pipeline.py

import pandas as pd
from utils.file_io import load_inputs
from utils.interpolation import interpolate_di_surface
from config import CONFIG


def test_load_and_interpolate_produces_non_empty_surface():
    surface, _, _ = load_inputs(CONFIG)
    yc_table = interpolate_di_surface(surface, CONFIG["TENORS"])

    assert not yc_table.empty, "A curva interpolada está vazia"
    assert "curve_id" in yc_table.columns or yc_table.index.name == "curve_id", "Coluna ou índice 'curve_id' ausente"
