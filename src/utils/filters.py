# utils/filters.py
import pandas as pd
from pathlib import Path
from src.config import CONFIG

def filter_corporate_universe(df: pd.DataFrame, inflation_linked: str = "N") -> pd.DataFrame:
    df = df.copy()
    print(f"🔍 Inicial: {len(df)} linhas")

    # Load valid bond IDs with prices
    price_ids = get_ids_with_prices(CONFIG["YA_PATH"])
    df["id"] = df["id"].astype(str).str.strip()
    df = df[df["id"].isin(price_ids)]
    print(f"✅ Após cruzar com YA: {len(df)}")

    df = df[~df['CLASSIFICATION_LEVEL_4_NAME'].str.startswith("Government", na=False)]
    print(f"➡ Após remover 'Government': {len(df)}")

    df = df[~df['industry_sector'].isin(['Financial'])]
    print(f"➡ Após remover 'Financial': {len(df)}")

    df = df[df['CPN_TYP'].isin(['FIXED'])]
    print(f"➡ Após filtrar CPN_TYP='FIXED': {len(df)}")

    df = df[df['CRNCY'].isin(['BRL'])]
    print(f"➡ Após filtrar CRNCY='BRL': {len(df)}")

    print("🧪 Valores únicos em INFLATION_LINKED_INDICATOR:", df["INFLATION_LINKED_INDICATOR"].unique())
    df["INFLATION_LINKED_INDICATOR"] = (
        df["INFLATION_LINKED_INDICATOR"]
        .astype(str)
        .str.strip()
        .str.upper()
    )
    print("🧪 Valores únicos normalizados em INFLATION_LINKED_INDICATOR:", df["INFLATION_LINKED_INDICATOR"].unique())
    df = df[df["INFLATION_LINKED_INDICATOR"] == inflation_linked.strip().upper()]
    print(f"➡ Após filtrar INFLATION_LINKED_INDICATOR={inflation_linked}: {len(df)}")

    df['TOT_DEBT_TO_EBITDA'] = pd.to_numeric(df['TOT_DEBT_TO_EBITDA'], errors='coerce')
    print(f"➡ Após conversão de TOT_DEBT_TO_EBITDA (com NaN): {df['TOT_DEBT_TO_EBITDA'].isna().sum()} NaNs")
    df = df[df['TOT_DEBT_TO_EBITDA'].notna()]
    print(f"➡ Após remover TOT_DEBT_TO_EBITDA nulos: {len(df)}")

    df["MATURITY"] = pd.to_datetime(df["MATURITY"], errors='coerce')
    return df


def get_ids_with_prices(price_file_path: Path) -> set:
    """Retorna um conjunto de IDs que possuem preços disponíveis
       Ignora ativos que não são precificados pela ANBIMA, portanto, não existem informações relacionadas aos preços e taxas indicativas.
    """
    df = pd.read_excel(price_file_path, sheet_name="ya_values_only", usecols="A")

    ya = df.dropna(subset=["YIELD"])
    ids_com_precos = ya["id"].astype(str).str.strip().unique()
    print(f"🔍 IDs com pelo menos um preço (YA): {len(ids_com_precos)}")

    df["id"] = df["id"].astype(str).str.strip()
    df = df[df["id"].isin(ids_com_precos)]
    print(f"✅ Após cruzar com YA: {len(df)}")

    return set(df)


def anomaly_filtering_results(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica filtros-padrão para selecionar o universo de bonds corporativos:
    - Exclui anomalias (bonds com corp yield igual a zero or crazy spreads)
    """
    df = df.copy()
    df = df[df["YAS_BOND_YLD"] != 0]
    df = df[(df["SPREAD"] >= -10) & (df["SPREAD"] <= 10)]
    return df
