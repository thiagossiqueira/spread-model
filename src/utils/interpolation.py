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

        # Usar ticker e data como identificador único
        ticker = grp["id"].iloc[0]
        date_key = obs_date.strftime("%Y%m%d")
        curve_id = f"{ticker}{date_key}"

        for tenor_label, t in tenors.items():
            rows.append({
                "curve_id": curve_id,
                "DATE": obs_date,
                "TENOR_LABEL": tenor_label,
                "TENOR": t,
                "YIELD": flat_forward_interpolation(t, curva)
            })

    df = pd.DataFrame(rows)
    return df.set_index("curve_id").sort_values(["DATE", "TENOR"])

def interpolate_yield_for_tenor(obs_date, yc_table, target_tenor, tenors):
    di_row = yc_table.loc[obs_date]
    curva = pd.Series(di_row.values, index=[tenors[k] for k in di_row.index])
    return flat_forward_interpolation(target_tenor, curva)
