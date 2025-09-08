# src/utils/file_io.py

import pandas as pd

def load_yield_surface(path):
    df = pd.read_excel(path, sheet_name="ya_values_only")
    df.rename(columns={df.columns[0]: "OBS_DATE"}, inplace=True)
    df["OBS_DATE"] = pd.to_datetime(df["OBS_DATE"])
    df = df.set_index("OBS_DATE").sort_index()

    # Manter " Corp" nos IDs
    df.columns = df.columns.astype(str).str.strip()
    return df

def load_corp_bond_data(path):
    df = pd.read_excel(path, sheet_name="db_values_only")
    df["id"] = df["id"].astype(str).str.strip()
    df = df.drop_duplicates(subset=["id"])
    return df

def load_di_surface(path):
    curve_df = pd.read_excel(path, sheet_name="only_values")
    curve_df["Curve date"] = pd.to_datetime(curve_df["Curve date"])

    surface = curve_df.rename(columns={
        "Curve date": "obs_date",
        "Generic ticker": "generic_ticker_id",
        "Term": "tenor",
        "px_last": "yield"
    })[["obs_date", "generic_ticker_id", "yield", "tenor"]].copy()

    if "volume" in curve_df.columns:
        surface["volume"] = pd.to_numeric(curve_df["volume"], errors="coerce")
        surface = surface.dropna(subset=["volume"])
        surface = surface[surface["volume"] > 1000]

    surface = surface.dropna(subset=["yield", "tenor"])
    surface = surface[surface["yield"] > 0]
    surface["curve_id"] = surface["generic_ticker_id"] + surface["obs_date"].dt.strftime("%Y%m%d")
    surface = surface.drop_duplicates(subset=["curve_id"], keep="last")

    return surface

def load_ipca_surface(path):
    df = pd.read_excel(path, sheet_name="only_values")
    df["Curve date"] = pd.to_datetime(df["Curve date"])

    surface = df.rename(columns={
        "Curve date": "obs_date",
        "Generic ticker": "generic_ticker_id",
        "Term": "tenor",
        "px_last": "yield"
    })[["obs_date", "generic_ticker_id", "yield", "tenor"]].copy()

    surface = surface.dropna(subset=["yield", "tenor"])
    surface = surface[surface["yield"] > 0]
    surface["curve_id"] = surface["generic_ticker_id"] + surface["obs_date"].dt.strftime("%Y%m%d")
    surface = surface.drop_duplicates(subset=["curve_id"], keep="last")

    return surface
