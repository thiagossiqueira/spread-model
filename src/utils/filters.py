# utils/filters.py
import pandas as pd


def filter_corporate_universe(df: pd.DataFrame, inflation_linked: str = "N") -> pd.DataFrame:
    df = df.copy()
    print(f"🔍 Inicial: {len(df)} linhas")

    df = df[~df['CLASSIFICATION_LEVEL_4_NAME'].str.startswith("Government", na=False)]
    print(f"➡ Após remover 'Government': {len(df)}")

    df = df[~df['industry_sector'].isin(['Financial'])]
    print(f"➡ Após remover 'Financial': {len(df)}")

    df = df[df['CPN_TYP'].isin(['FIXED'])]
    print(f"➡ Após filtrar CPN_TYP='FIXED': {len(df)}")

    # df = df[df['MTY_TYP'].isin(['AT MATURITY'])]
    # print(f"➡ Após filtrar MTY_TYP='AT MATURITY': {len(df)}")

    df = df[df['CRNCY'].isin(['BRL'])]
    print(f"➡ Após filtrar CRNCY='BRL': {len(df)}")

    df = df[df['INFLATION_LINKED_INDICATOR'].isin([inflation_linked])]
    print(f"➡ Após filtrar INFLATION_LINKED_INDICATOR={inflation_linked}: {len(df)}")

    df['TOT_DEBT_TO_EBITDA'] = pd.to_numeric(df['TOT_DEBT_TO_EBITDA'], errors='coerce')
    print(f"➡ Após conversão de TOT_DEBT_TO_EBITDA (com NaN): {df['TOT_DEBT_TO_EBITDA'].isna().sum()} NaNs")

    df = df[df['TOT_DEBT_TO_EBITDA'].notna()]
    print(f"➡ Após remover TOT_DEBT_TO_EBITDA nulos: {len(df)}")

    df["MATURITY"] = pd.to_datetime(df["MATURITY"], errors='coerce')
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
