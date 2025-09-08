import pandas as pd
from calendars.daycounts import DayCounts
from config import CONFIG
#from utils.file_io import load_inputs
from src.utils.file_io import (
load_corp_bond_data,
load_yield_surface,
load_di_surface,
load_ipca_surface,
)
dc = DayCounts("bus/252", calendar="cdr_anbima")

def test_taxas_e_terms_corretos_para_2025_06_30():

    surface = load_di_surface(CONFIG["HIST_CURVE_PATH"])
    surface = surface.reset_index(drop=True)
    surface = surface[surface["obs_date"] == pd.Timestamp("2025-06-30")].copy()
    surface["curve_id"] = surface["generic_ticker_id"] + surface["obs_date"].dt.strftime("%Y%m%d")
    surface = surface.set_index("curve_id")

    tickers = [
        "od1 Comdty", "od2 Comdty", "od3 Comdty", "od4 Comdty", "od5 Comdty",
        "od6 Comdty", "od7 Comdty", "od8 Comdty", "od9 Comdty", "od10 Comdty",
        "od11 Comdty", "od12 Comdty", "od13 Comdty", "od16 Comdty", "od18 Comdty",
        "od19 Comdty", "od20 Comdty", "od22 Comdty", "od23 Comdty", "od24 Comdty",
        "od25 Comdty", "od26 Comdty", "od27 Comdty", "od28 Comdty", "od29 Comdty",
        "od30 Comdty", "od31 Comdty", "od32 Comdty", "od33 Comdty", "od35 Comdty",
        "od36 Comdty", "od37 Comdty", "od38 Comdty", "od39 Comdty", "od40 Comdty",
        "od41 Comdty", "od42 Comdty", "od43 Comdty"
    ]

    taxas_esperadas = [
        14.9, 14.907, 14.923, 14.933, 14.933,
        14.933, 14.928, 14.918, 14.897, 14.861,
        14.809, 14.748, 14.675, 14.396, 14.092,
        13.846, 13.607, 13.417, 13.251, 13.148,
        13.097, 13.083, 13.07, 13.067, 13.094,
        13.094, 13.116, 13.126, 13.147, 13.185,
        13.265, 13.286, 13.274, 13.289, 13.264,
        13.243, 13.19, 13.137
    ]

    terms_esperados = [
        0.087301587, 0.174603175, 0.261904762, 0.349206349, 0.428571429,
        0.511904762, 0.599206349, 0.670634921, 0.753968254, 0.837301587,
        0.916666667, 1.0, 1.087301587, 1.341269841, 1.5,
        1.583333333, 1.654761905, 1.825396825, 1.900793651, 1.992063492,
        2.079365079, 2.162698413, 2.25, 2.329365079, 2.408730159,
        2.496031746, 2.579365079, 2.658730159, 2.746031746, 2.904761905,
        2.992063492, 3.071428571, 3.162698413, 3.246031746, 3.325396825,
        3.404761905, 3.484126984, 3.567460317
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
