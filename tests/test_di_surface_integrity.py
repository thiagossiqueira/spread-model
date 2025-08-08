import pandas as pd
from calendars.daycounts import DayCounts
from config import CONFIG
from utils.file_io import load_inputs

dc = DayCounts("bus/252", calendar="cdr_anbima")

def test_valores_para_contratos_od1_od5_od9():
    surface, _, _ = load_inputs(CONFIG)

    df = surface[surface["obs_date"].isin([
        pd.Timestamp("2025-04-30"),
        pd.Timestamp("2025-05-30"),
        pd.Timestamp("2025-06-30")
    ])].copy()

    df["curve_id"] = df["generic_ticker_id"] + df["obs_date"].dt.strftime("%Y%m%d")
    df = df.set_index("curve_id")

    contratos_esperados = {
        "od1 Comdty20250430": (14.15, 0.083333333),
        "od1 Comdty20250530": (14.65, 0.079365079),
        "od1 Comdty20250630": (14.90, 0.087301587),
        "od5 Comdty20250430": (14.633, 0.424603175),
        "od5 Comdty20250530": (14.771, 0.432539683),
        "od5 Comdty20250630": (14.933, 0.428571429),
        "od9 Comdty20250430": (14.659, 0.761904762),
        "od9 Comdty20250530": (14.787, 0.75),
        "od9 Comdty20250630": (14.897, 0.753968254)
    }

    for cid, (taxa, tenor) in contratos_esperados.items():
        assert cid in df.index, f"{cid} não encontrado"
        row = df.loc[cid]
        assert round(row["yield"], 6) == round(taxa, 6), f"Taxa incorreta para {cid}"
        assert round(row["tenor"], 6) == round(tenor, 6), f"Tenor incorreto para {cid}"
