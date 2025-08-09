import numpy as np
import pandas as pd
from finmath.termstructure.curve_models import flat_forward_interpolation


def interpolate_di_surface(surface: pd.DataFrame, tenors: dict) -> pd.DataFrame:
    return interpolate_surface(surface, tenors)


def interpolate_surface(surface: pd.DataFrame, tenors: dict, min_points: int = 2) -> pd.DataFrame:
    """
    Interpola a superfície de rendimento com base nos tenores alvo.

    Args:
        surface (pd.DataFrame): DataFrame com colunas ['obs_date', 'tenor', 'yield']
        tenors (dict): Mapeamento do nome do tenor para seu valor em anos
        min_points (int): Mínimo de pontos para realizar interpolação (default=2)

    Returns:
        pd.DataFrame: DataFrame indexado por obs_date, colunas = tenores alvo
    """
    rows = []
    surface["obs_date"] = pd.to_datetime(surface["obs_date"])

    for obs_date, grp in surface.groupby("obs_date"):
        curva = pd.Series(grp["yield"].values, index=grp["tenor"].values).dropna()
        if len(curva) < min_points:
            continue
        interpolated = {k: flat_forward_interpolation(t, curva) for k, t in tenors.items()}
        rows.append({"obs_date": obs_date, **interpolated})

    result = pd.DataFrame(rows)
    if result.empty:
        raise ValueError("interpolate_surface() retornou DataFrame vazio!")

    return result.set_index("obs_date").sort_index()


def interpolate_yield_for_tenor(obs_date, yc_table, target_tenor, tenors, curve_id):
    di_row = yc_table.loc[curve_id]
    if "obs_date" in di_row.index:
        di_row = di_row.drop("obs_date")
    curva = pd.Series(di_row.values, index=[tenors[k] for k in di_row.index])
    return flat_forward_interpolation(target_tenor, curva)