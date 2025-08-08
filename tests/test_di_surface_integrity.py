import pandas as pd
from calendars.daycounts import DayCounts
from config import CONFIG
from utils.file_io import load_inputs

dc = DayCounts("bus/252", calendar="cdr_anbima")

def test_taxas_e_terms_para_od1_od5_od9_em_tres_datas():
    surface, _, _ = load_inputs(CONFIG)

    surface = surface.reset_index(drop=True)
    surface["curve_id"] = surface["generic_ticker_id"] + surface["obs_date"].dt.strftime("%Y%m%d")
    surface = surface.set_index("curve_id")

    # ✅ Esperado: 3 tickers × 3 datas = 9 casos
    entradas = [
        # od1
        ("od1 Comdty", "20250430", 14.15, 0.083333333),
        ("od1 Comdty", "20250530", 14.65, 0.079365079),
        ("od1 Comdty", "20250630", 14.90, 0.087301587),

        # od5
        ("od5 Comdty", "20250430", 14.633, 0.424603175),
        ("od5 Comdty", "20250530", 14.771, 0.432539683),
        ("od5 Comdty", "20250630", 14.933, 0.428571429),

        # od9
        ("od9 Comdty", "20250430", 14.659, 0.761904762),
        ("od9 Comdty", "20250530", 14.787, 0.750),
        ("od9 Comdty", "20250630", 14.897, 0.753968254),
    ]

    for ticker, yyyymmdd, taxa_esp, term_esp in entradas:
        curve_id = ticker + yyyymmdd
        assert curve_id in surface.index, f"curve_id {curve_id} não encontrado"
        linha = surface.loc[curve_id]
        taxa_encontrada = float(linha["yield"])
        term_encontrado = linha["tenor"]
        assert round(taxa_encontrada, 4) == round(taxa_esp, 4), f"Taxa incorreta para {curve_id}"
        assert round(term_encontrado, 6) == round(term_esp, 6), f"Tenor incorreto para {curve_id}"
