# utils/interpolation.py
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

def interpolate_di_surface(surface: pd.DataFrame, tenors: dict) -> pd.DataFrame:
    rows = []
    for obs_date, grp in surface.groupby("obs_date"):
        grp = grp.drop_duplicates(subset="tenor").sort_values("tenor")
        if grp["tenor"].nunique() < 2:
            continue
        x = grp["tenor"].to_numpy()
        y = grp["yield"].to_numpy()
        f = interp1d(x, y, kind="linear", bounds_error=False, fill_value="extrapolate", assume_sorted=True)
        rows.append({"DATE": obs_date, **{k: float(f(t)) for k, t in tenors.items()}})

    return pd.DataFrame(rows).set_index("DATE").sort_index().dropna(how="any")

def interpolate_yield_for_tenor(obs_date, yc_table, target_tenor, tenors):
    di_row = yc_table.loc[obs_date]
    x = np.array([tenors[k] for k in di_row.index])
    y = di_row.values
    f = interp1d(x, y, kind="linear", bounds_error=False, fill_value="extrapolate")
    return float(f(target_tenor))
