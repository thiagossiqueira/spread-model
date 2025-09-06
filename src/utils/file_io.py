# src/utils/file_io.py
import pandas as pd
from src.config import CONFIG

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

    # NÃO remover " Corp" — IDs já estão padronizados
    df.columns = df.columns.astype(str).str.strip()
    return df

def load_corp_bond_data(path):
    df = pd.read_excel(path, sheet_name="db_values_only")
    df["id"] = df["id"].astype(str).str.strip()
    df = df.drop_duplicates(subset=["id"])
    return df

def load_inputs(config):
    # DI Surface
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

    # Load corp metadata + yields
    corp_data = load_corp_bond_data(config["CORP_PATH"])
    yields_ts = load_yield_surface(config["YA_PATH"])

    # Validar apenas os IDs com preços históricos
    valid_ids = set(yields_ts.columns)
    corp_data = corp_data[corp_data["id"].isin(valid_ids)]

    # 👇 Diagnóstico: exibir conteúdo das bases carregadas
    print("\n file_io.py: surface.tail(10):")
    print(surface.tail(10))

    print("\n file_io.py:  corp_data.tail(10):")
    print(corp_data.tail(10))

    print("\n file_io.py:  yields_ts.tail(10):")
    print(yields_ts.tail(10).iloc[:, :5])  # mostra só as 5 primeiras colunas para não estourar terminal

    return surface, corp_data, yields_ts
