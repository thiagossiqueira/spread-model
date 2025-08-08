import pandas as pd
from calendars.daycounts import DayCounts
from config import CONFIG
from utils.file_io import load_inputs

dc = DayCounts("bus/252", calendar="cdr_anbima")

def test_taxas_e_terms_para_contratos_od1_od5_od9():


    surface, _, _ = load_inputs(CONFIG)

    surface = surface.reset_index(drop=True)
    surface = surface[surface["obs_date"] == pd.Timestamp("2025-06-30")].copy()
    surface["curve_id"] = surface["generic_ticker_id"] + surface["obs_date"].dt.strftime("%Y%m%d")
    surface = surface.set_index("curve_id")

    dados_esperados = {
        "od1 Comdty": (14.9, 0.0873),
        "od5 Comdty": (14.933, 0.4286),
        "od9 Comdty": (14.897, 0.7540),
    }

    for ticker, (taxa_esp, tenor_esp) in dados_esperados.items():
        curve_id = ticker + "20250630"
        assert curve_id in surface.index, f"curve_id {curve_id} não encontrado"

        linha = surface.loc[curve_id]
        taxa_encontrada = float(linha["yield"])
        tenor_encontrado = float(linha["tenor"])

        assert round(taxa_encontrada, 4) == round(taxa_esp, 4), f"Taxa incorreta para {ticker}"
        assert round(tenor_encontrado, 4) == round(tenor_esp, 4), f"Tenor incorreto para {ticker}"
