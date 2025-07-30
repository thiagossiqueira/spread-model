import pandas as pd
from calendars.daycounts import DayCounts
from src.config import CONFIG
from src.utils.file_io import load_inputs

dc = DayCounts("bus/252", calendar="cdr_anbima")

def test_taxas_e_terms_corretos_para_2025_06_30():
    surface, _, _ = load_inputs(CONFIG)
    surface = surface[surface["obs_date"] == pd.Timestamp("2025-06-30")]

    tickers = [
        f"od{i} Comdty" for i in list(range(1, 14)) + [16, 17, 18, 19, 21, 22, 23, 24, 25,
                                                       26, 27, 28, 29, 30, 31, 32, 34, 35, 36, 37, 38, 39, 40, 41, 42]
    ]
    taxas_esperadas = [
        14.9, 14.907, 14.923, 14.933, 14.933, 14.933, 14.928, 14.918, 14.897, 14.861,
        14.809, 14.748, 14.675, 14.396, 14.092, 13.846, 13.607, 13.417, 13.251, 13.148,
        13.097, 13.083, 13.07, 13.067, 13.094, 13.094, 13.116, 13.126, 13.147, 13.185,
        13.265, 13.286, 13.274, 13.289, 13.264, 13.243, 13.19, 13.137
    ]
    terms_esperados = [
        0.1, 0.2, 0.3, 0.3, 0.4, 0.5, 0.6, 0.7, 0.7, 0.8, 0.9, 1.0, 1.1,
        1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.3, 2.4,
        2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2, 3.2, 3.3, 3.4, 3.5
    ]

    assert len(tickers) == len(taxas_esperadas) == len(terms_esperados)

    for ticker, taxa, term in zip(tickers, taxas_esperadas, terms_esperados):
        linha = surface[surface["id"] == ticker]
        assert not linha.empty, f"Ticker {ticker} não encontrado"
        taxa_encontrada = float(linha["yield"].iloc[0])
        dias_uteis = linha["tenor"].iloc[0]
        term_encontrado = dias_uteis / 252.0
        assert round(taxa_encontrada, 3) == round(taxa, 3), f"Taxa incorreta para {ticker}"
        assert round(term_encontrado, 2) == round(term, 2), f"Term incorreto para {ticker}"