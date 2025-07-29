# utils/interpolation.py
import numpy as np
import pandas as pd
from finmath.termstructure.curve_models import flat_forward_interpolation

def interpolate_di_surface(surface: pd.DataFrame, tenors: dict) -> pd.DataFrame:
    rows = []
    for obs_date, grp in surface.groupby("obs_date"):
        grp = grp.drop_duplicates(subset="tenor").sort_values("tenor")
        if grp["tenor"].nunique() < 2:
            continue
        x = grp["tenor"].to_numpy()
        y = grp["yield"].to_numpy()
        curva = pd.Series(y, index=x)
        rows.append({"DATE": obs_date, **{k: flat_forward_interpolation(t, curva) for k, t in tenors.items()}})

    return pd.DataFrame(rows).set_index("DATE").sort_index().dropna(how="any")

def interpolate_yield_for_tenor(obs_date, yc_table, target_tenor, tenors):
    di_row = yc_table.loc[obs_date]
    curva = pd.Series(di_row.values, index=[tenors[k] for k in di_row.index])
    return flat_forward_interpolation(target_tenor, curva)
