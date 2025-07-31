# tests/test_di_surface_integrity.py
import pandas as pd
from calendars.daycounts import DayCounts
from config import CONFIG
from utils.file_io import load_inputs

dc = DayCounts("bus/252", calendar="cdr_anbima")

def test_taxas_e_terms_corretos_para_2025_06_30():
    surface, _, _ = load_inputs(CONFIG)
    surface = surface[surface["obs_date"] == pd.Timestamp("2025-06-30")]
    surface = surface.copy()  # já está com curve_id como índice

    tickers = [
        f"od{i} Comdty" for i in list(range(1, 14)) + [16, 17, 18, 19, 21, 22, 23, 24, 25,
                                                       26, 27, 28, 29, 30, 31, 32, 34, 35, 36, 37, 38, 39, 40, 41, 42]
    ]
    taxas_esperadas = [
        14.9000, 14.9070, 14.9230, 14.9330, 14.9330, 14.9330, 14.9280, 14.9180,
        14.8970, 14.8610, 14.8090, 14.7480, 14.6750, 14.3960, 14.0920, 13.8460,
        13.6070, 13.4170, 13.2510, 13.1480, 13.0970, 13.0830, 13.0700, 13.0670,
        13.0940, 13.0940, 13.1160, 13.1260, 13.1470, 13.1850, 13.2650, 13.2860,
        13.2740, 13.2890, 13.2640, 13.2430, 13.1900, 13.1370
    ]
    terms_esperados = [
        0.0873, 0.1746, 0.2619, 0.3492, 0.4286, 0.5119, 0.5992, 0.6706, 0.7540, 0.8373, 0.9167, 1.0, 1.0873,
        1.3413, 1.4167, 1.5, 1.5833, 1.7381, 1.8254, 1.9008, 1.9921, 2.0794, 2.1627, 2.25, 2.3294, 2.4087,
        2.4960, 2.5794, 2.6587, 2.8214, 2.9048, 2.9921, 3.0714, 3.1627, 3.2460, 3.3254, 3.4048, 3.4841
    ]

    assert len(tickers) == len(taxas_esperadas) == len(terms_esperados)

    for ticker, taxa, term in zip(tickers, taxas_esperadas, terms_esperados):
        curve_id = ticker + "20250630"
        assert curve_id in surface.index, f"curve_id {curve_id} não encontrado"
        linha = surface.loc[curve_id]
        taxa_encontrada = float(linha["yield"])
        dias_uteis = linha["tenor"]
        term_encontrado = dias_uteis / 252.0
        assert round(taxa_encontrada, 4) == round(taxa, 4), f"Taxa incorreta para {ticker}"
        assert round(term_encontrado, 4) == round(term, 4), f"Term incorreto para {ticker}"
