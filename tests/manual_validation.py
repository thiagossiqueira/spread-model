import pandas as pd
import numpy as np
from config import CONFIG
from src.utils.file_io import load_inputs
from src.utils.interpolation import interpolate_di_surface
from scipy.interpolate import interp1d

bond_id = "BI018411"
fecha_obs = pd.Timestamp("2025-06-30")


def test_bono_aparece_despues_de_filtrado():
    _, corp_base, _ = load_inputs(CONFIG)
    assert bond_id in corp_base["id"].values


def test_yield_observado_presente_en_dataframe():
    _, _, yields_ts = load_inputs(CONFIG)
    assert not pd.isna(yields_ts.at[fecha_obs, bond_id])


def test_calculo_de_tenor_en_anios():
    _, corp_base, _ = load_inputs(CONFIG)
    bono = corp_base[corp_base["id"] == bond_id].iloc[0]
    tenor = (bono["MATURITY"] - fecha_obs).days / 365.25
    assert round(tenor, 2) == 4.55


def test_interpolacion_curva_DI():
    surface, _, _ = load_inputs(CONFIG)
    yc_table = interpolate_di_surface(surface, CONFIG["TENORS"])
    di_row = yc_table.loc[fecha_obs]
    x = np.array([CONFIG["TENORS"][k] for k in di_row.index])
    y = di_row.values
    f = interp1d(x, y, kind="linear", bounds_error=False, fill_value="extrapolate")
    rendimiento_interpolado = float(f(4.55))

    assert round(rendimiento_interpolado, 3) == 13.137


def test_calculo_del_spread_final():
    _, _, yields_ts = load_inputs(CONFIG)
    rendimiento_bono = yields_ts.at[fecha_obs, bond_id]
    rendimiento_di = 13.137
    spread = rendimiento_bono - rendimiento_di

    assert round(rendimiento_bono, 2) == 12.32
    assert round(spread * 100, 2) == -81.92
