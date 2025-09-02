# utils/filters.py
import pandas as pd

def filter_corporate_universe(df: pd.DataFrame, inflation_linked: str = "N") -> pd.DataFrame:
    """
    Aplica filtros-padrão para selecionar o universo de bonds corporativos:
    - Exclui títulos governamentais e financeiros
    - Considera apenas cupons FIXED, vencimento 'AT MATURITY'
    - Apenas BRL e com indicador de indexação inflacionária (INFLATION_LINKED_INDICATOR = 'Y') ou não
    """

    df = df.copy()
    df = df[~df['CLASSIFICATION_LEVEL_4_NAME'].str.startswith("Government", na=False)]
    df = df[~df['industry_sector'].isin(['Financial'])]
    df = df[df['CPN_TYP'].isin(['FIXED'])]
    df = df[df['MTY_TYP'].isin(['AT MATURITY'])]
    df = df[df['CRNCY'].isin(['BRL'])]
    df = df[df['INFLATION_LINKED_INDICATOR'].isin([inflation_linked])]
    df['TOT_DEBT_TO_EBITDA'] = pd.to_numeric(df['TOT_DEBT_TO_EBITDA'], errors='coerce')
    df = df[df['TOT_DEBT_TO_EBITDA'].notna()]
    df["MATURITY"] = pd.to_datetime(df["MATURITY"])
    df["id"] = df["id"].astype(str).str.strip()
    return df


# utils/filters.py

def anomaly_filtering_results(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica filtros-padrão para selecionar o universo de bonds corporativos:
    - Exclui anomalias (bonds com corp yield igual a zero or crazy spreads)
    """
    df = df.copy()
    df = df[df["YAS_BOND_YLD"] != 0]
    df = df[(df["SPREAD"] >= -10) & (df["SPREAD"] <= 10)]
    return df
