import numpy as np
import pandas as pd
from finmath.termstructure.curve_models import flat_forward_interpolation

def interpolate_di_surface(surface: pd.DataFrame, tenors: dict) -> pd.DataFrame:
    surface = surface.copy()
    surface["curve_id"] = surface["generic_ticker_id"] + surface["obs_date"].dt.strftime("%Y%m%d")

    rows = []
    for curve_id, grp in surface.groupby("curve_id"):
        grp = grp.drop_duplicates(subset="tenor").sort_values("tenor")
        if grp["tenor"].nunique() < 2:
            continue  # ignora curvas com menos de 2 pontos
        x = grp["tenor"].to_numpy()
        y = grp["yield"].to_numpy()
        curva = pd.Series(y, index=x)
        obs_date = grp["obs_date"].iloc[0]
        rows.append({
            "curve_id": curve_id,
            "obs_date": obs_date,
            **{k: flat_forward_interpolation(t, curva) for k, t in tenors.items()}
        })

    result = pd.DataFrame(rows)
    if result.empty:
        raise ValueError("interpolate_di_surface() retornou DataFrame vazio!")

    result = result.set_index("curve_id").sort_index()
    return result



def interpolate_yield_for_tenor(obs_date, yc_table, target_tenor, tenors, curve_id):
    di_row = yc_table.loc[curve_id]
    if "obs_date" in di_row.index:
        di_row = di_row.drop("obs_date")
    curva = pd.Series(di_row.values, index=[tenors[k] for k in di_row.index])
    return flat_forward_interpolation(target_tenor, curva)