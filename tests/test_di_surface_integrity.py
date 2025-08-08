import pandas as pd
from calendars.daycounts import DayCounts
from config import CONFIG
from utils.file_io import load_inputs

dc = DayCounts("bus/252", calendar="cdr_anbima")

def test_taxas_e_terms_corretos_para_2025_06_30():
    surface, _, _ = load_inputs(CONFIG)

    surface = surface.reset_index(drop=True)
    surface = surface[surface["obs_date"] == pd.Timestamp("2025-06-30")].copy()
    surface["curve_id"] = surface["generic_ticker_id"] + surface["obs_date"].dt.strftime("%Y%m%d")
    surface = surface.set_index("curve_id")

    tickers = [
        f"od{i} Comdty" for i in [1, 5, 9]
    ]

    taxas_esperadas = [
        14.15, 14.65, 14.9,
        14.633, 14.771, 14.933,
        14.659, 14.787, 14.897
    ]
    terms_esperados = [
        0.083333333, 0.079365079, 0.087301587,
        0.424603175, 0.432539683, 0.428571429,
        0.761904762, 0.75, 0.753968254
    ]


    assert len(tickers) == len(taxas_esperadas) == len(terms_esperados)

    for ticker, taxa, term in zip(tickers, taxas_esperadas, terms_esperados):
        curve_id = ticker + "20250630"
        assert curve_id in surface.index, f"curve_id {curve_id} não encontrado"
        linha = surface.loc[[curve_id]]
        taxa_encontrada = float(linha["yield"].iloc[0])
        term_encontrado = linha["tenor"].iloc[0]
        assert round(taxa_encontrada, 4) == round(taxa, 4), f"Taxa incorreta para {ticker}"
        assert round(term_encontrado, 4) == round(term, 4), f"Term incorreto para {ticker}"