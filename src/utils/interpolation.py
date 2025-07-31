# utils/interpolation.py
import numpy as np
import pandas as pd
from finmath.termstructure.curve_models import flat_forward_interpolation


def interpolate_di_surface(surface: pd.DataFrame, tenors: dict) -> pd.DataFrame:
    """
    Constrói uma tabela com os yields interpolados para cada data de observação
    e para cada tenor definido, utilizando interpolação flat-forward (ANBIMA).
    """
    rows = []

    for obs_date, grp in surface.groupby("obs_date"):
        # Remove possíveis duplicatas no mesmo dia e ordena por tenor
        grp = grp.drop_duplicates(subset="tenor").sort_values("tenor")
        if grp["tenor"].nunique() < 2:
            continue  # Ignora dias com menos de 2 pontos distintos

        curva = pd.Series(grp["yield"].values, index=grp["tenor"].values).astype(float)

        interpolated = {k: flat_forward_interpolation(t, curva) for k, t in tenors.items()}
        rows.append({"DATE": obs_date, **interpolated})

    return pd.DataFrame(rows).set_index("DATE").sort_index().dropna(how="any")


def interpolate_yield_for_tenor(obs_date, yc_table, target_tenor, tenors):
    """
    Interpola a curva DI para um tenor alvo em uma data de observação específica.
    """
    di_row = yc_table.loc[obs_date]
    curva = pd.Series(di_row.values, index=[tenors[k] for k in di_row.index]).astype(float)
    return flat_forward_interpolation(target_tenor, curva)
