# utils/file_io.py
import pandas as pd

def load_di_futures(path):
    df = pd.read_excel(path, sheet_name="periods_values_only")
    df["End of Month date"] = pd.to_datetime(df["End of Month date"])
    df["Settlement date"] = pd.to_datetime(df["Settlement date"])
    return df

def load_yield_surface(path):
    df = pd.read_excel(path, sheet_name="ya_values_only")
    df.rename(columns={df.columns[0]: "OBS_DATE"}, inplace=True)
    df["OBS_DATE"] = pd.to_datetime(df["OBS_DATE"])
    df = df.set_index("OBS_DATE").sort_index()

    # Corrigir colunas: remover " Corp" para padronizar com universo
    df.columns = df.columns.astype(str).str.strip().str.replace(" Corp", "", regex=False)

    return df

def load_corp_bond_data(path):
    df = pd.read_excel(path, sheet_name="db_values_only")
    df["id"] = df["id"].astype(str).str.strip()
    df["MATURITY"] = pd.to_datetime(df["MATURITY"], errors='coerce')
    return df

def load_inputs(config):
    # DI surface
    curve_df = pd.read_excel(config["HIST_CURVE_PATH"], sheet_name="only_values")
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
        surface = surface[surface["volume"] > 0]

    surface = surface.dropna(subset=["yield", "tenor"])
    surface = surface[surface["yield"] > 0]
    surface["curve_id"] = surface["generic_ticker_id"] + surface["obs_date"].dt.strftime("%Y%m%d")
    surface = surface.drop_duplicates(subset=["curve_id"], keep="last")

    # Load corp metadata and prices
    corp_data = load_corp_bond_data(config["CORP_PATH"])
    yields_ts = load_yield_surface(config["YA_PATH"])

    # crucial: Normalizar ids e cruzar com preços
    corp_data["id"] = corp_data["id"].astype(str).str.strip()
    valid_ids = set(yields_ts.columns)
    corp_data = corp_data[corp_data["id"].isin(valid_ids)]

    return surface, corp_data, yields_ts