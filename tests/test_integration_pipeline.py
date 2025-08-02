# tests/test_integration_pipeline.py

import pytest
from src.utils.file_io import load_inputs
from src.utils.interpolation import interpolate_di_surface
from src.config import CONFIG


def test_pipeline_load_inputs_and_interpolation():
    surface, _, _ = load_inputs(CONFIG)

    assert not surface.empty, "Surface carregada está vazia!"

    # Executa a interpolação com os tenores definidos na config
    interpolated = interpolate_di_surface(surface, CONFIG["TENORS"])

    assert not interpolated.empty, "Resultado da interpolação está vazio!"
    assert "curve_id" in interpolated.columns or interpolated.index.name == "curve_id", "Coluna ou índice 'curve_id' ausente"

    # Verifica se todas as colunas de tenores esperados foram geradas
    for tenor_label in CONFIG["TENORS"].keys():
        assert tenor_label in interpolated.columns, f"Tenor esperado '{tenor_label}' ausente na interpolação"

    print(f"✅ Interpolação executada com sucesso para {len(interpolated)} curvas.")