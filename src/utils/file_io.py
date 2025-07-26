# utils/file_io.py
import pandas as pd
from config import CONFIG

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
    return df

def load_corp_bond_data(path):
    df = pd.read_excel(path, sheet_name="db_values_only")
    df = df[~df['CLASSIFICATION_LEVEL_4_NAME'].str.startswith("Government", na=False)]
    df = df[~df['industry_sector'].isin(['Financial'])]
    df = df[df['CPN_TYP'].isin(['FIXED'])]
    df = df[df['MTY_TYP'].isin(['AT MATURITY'])]
    df = df[df['CRNCY'].isin(['BRL'])]
    df['TOT_DEBT_TO_EBITDA'] = pd.to_numeric(df['TOT_DEBT_TO_EBITDA'], errors='coerce')
    df = df[df['TOT_DEBT_TO_EBITDA'].notna()]
    df = df[df['INFLATION_LINKED_INDICATOR'].isin(['Y'])]
    df["MATURITY"] = pd.to_datetime(df["MATURITY"])
    df["id"] = df["id"].astype(str).str.strip()
    return df

def load_inputs(config):
    bonds_static = load_di_futures(config["DI_PATH"])
    ylds = load_yield_surface(config["YIELD_PATH"])
    bonds_key = bonds_static[["Generic ticker", "Curve date", "End of Month days"]]
    bonds_key = bonds_key.rename(columns={"Curve date": "OBS_DATE"})

    long = (
        ylds.reset_index()
            .melt(id_vars="OBS_DATE", var_name="Generic ticker", value_name="yield")
            .dropna(subset=["yield"])
            .loc[lambda df: df["yield"] > 0]
    )
    merged = long.merge(bonds_key, on=["Generic ticker", "OBS_DATE"], how="left")
    surface = merged.rename(columns={"OBS_DATE": "obs_date", "Generic ticker": "id", "End of Month days": "tenor"})[
        ["obs_date", "id", "yield", "tenor"]
    ].reset_index(drop=True)

    corp_data = load_corp_bond_data(config["CORP_PATH"])
    yields_ts = load_yield_surface(config["YA_PATH"])
    yields_ts.columns = yields_ts.columns.astype(str).str.strip()
    corp_data = corp_data[corp_data["id"].isin(yields_ts.columns)]

    return surface, corp_data, yields_ts
