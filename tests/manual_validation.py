import pandas as pd
import numpy as np
from src.config import CONFIG
#from src.utils.file_io import load_inputs
from src.utils.file_io import (
load_corp_bond_data,
load_yield_surface,
load_di_surface,
load_ipca_surface,
)
from src.utils.interpolation import interpolate_di_surface
from calendars.daycounts import DayCounts
from finmath.curve_models import flat_forward_interpolation

bond_id = "BI018411"
fecha_obs = pd.Timestamp("2025-06-30")
DAYCOUNT = DayCounts("bus/252", calendar="cdr_anbima")

def test_bono_aparece_despues_de_filtrado():
    _, corp_base, _ = load_corp_bond_data(CONFIG["CORP_PATH"])
    assert bond_id in corp_base["id"].values

def test_yield_observado_presente_en_dataframe():
    _, _, yields_ts = load_yield_surface(CONFIG["YA_PATH"])
    assert not pd.isna(yields_ts.at[fecha_obs, bond_id])

def test_calculo_de_tenor_en_anios():
    _, corp_base, _ = load_corp_bond_data(CONFIG["CORP_PATH"])
    bono = corp_base[corp_base["id"] == bond_id].iloc[0]
    tenor = DAYCOUNT.diff_in_years(fecha_obs, bono["MATURITY"])
    assert round(tenor, 8) == 4.51984127

def test_interpolacion_curva_DI():
    surface, _, _ = load_di_surface(CONFIG["HIST_CURVE_PATH"])
    yc_table = interpolate_di_surface(surface, CONFIG["TENORS"])
    di_row = yc_table.loc[fecha_obs]
    curva = pd.Series(di_row.values, index=[CONFIG["TENORS"][k] for k in di_row.index])
    rendimiento_interpolado = flat_forward_interpolation(4.51984127, curva)

    assert round(rendimiento_interpolado, 3) == 13.137

def test_calculo_del_spread_final():
    _, _, yields_ts = load_yield_surface(CONFIG["YA_PATH"])
    rendimiento_bono = yields_ts.at[fecha_obs, bond_id]
    rendimiento_di = 13.137
    spread = rendimiento_bono - rendimiento_di

    assert round(rendimiento_bono, 2) == 12.32
    assert round(spread * 100, 2) == -81.92
