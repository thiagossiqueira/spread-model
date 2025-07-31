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
    # Load DI curve data from new consolidated file
    curve_df = pd.read_excel(config["HIST_CURVE_PATH"], sheet_name="only_values")
    curve_df["Curve date"] = pd.to_datetime(curve_df["Curve date"])

    surface = curve_df.rename(columns={
        "Curve date": "obs_date",
        "Generic ticker": "id",
        "Term": "tenor",
        "px_last": "yield"
    })[["obs_date", "id", "yield", "tenor"]].copy()

    surface = surface.dropna(subset=["yield", "tenor"])
    surface = surface[surface["yield"] > 0]

    # Diagnóstico: verificar duplicatas antes do drop_duplicates
    dups = surface[surface.duplicated(subset=["obs_date", "id"], keep=False)]
    if not dups.empty:
        print("\n🚨 Duplicatas encontradas na curva DI consolidada:")
        print(f"📄 Arquivo: {config['HIST_CURVE_PATH']}")
        print(dups.sort_values(["obs_date", "id"]))
        raise ValueError("❌ Ainda há duplicatas em ['obs_date', 'id'] antes do drop_duplicates.")

    # Remove duplicatas por data e ticker, se ainda houver
    surface = surface.drop_duplicates(subset=["obs_date", "id"], keep="last")

    # Load corporate bond metadata
    corp_data = load_corp_bond_data(config["CORP_PATH"])

    # Load corporate yield time series
    yields_ts = load_yield_surface(config["YA_PATH"])
    yields_ts.columns = yields_ts.columns.astype(str).str.strip()

    # Keep only bonds with matching time series
    corp_data = corp_data[corp_data["id"].isin(yields_ts.columns)]

    return surface, corp_data, yields_ts
