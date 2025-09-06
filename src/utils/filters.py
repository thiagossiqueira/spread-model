# src/utils/filters.py
import pandas as pd

def filter_corporate_universe(df: pd.DataFrame, inflation_linked: str = "N", calc_typ_valid: list[int] = None) -> pd.DataFrame:
    df = df.copy()
    print(f"🔍 Inicial: {len(df)} linhas")

    # 1. Filtro por tipo de curva (CALC_TYP)
    if calc_typ_valid is not None:
        df = df[df["CALC_TYP"].isin(calc_typ_valid)]
        print(f"➡ Após filtrar CALC_TYP {calc_typ_valid}: {len(df)}")

    # 2. Remover governamentais e financeiros
    df = df[~df["CLASSIFICATION_LEVEL_4_NAME"].str.startswith("Government", na=False)]
    print(f"➡ Após remover 'Government': {len(df)}")

    df = df[~df["industry_sector"].isin(["Financial"])]
    print(f"➡ Após remover 'Financial': {len(df)}")

    # 3. Apenas cupom fixo, BRL
    df = df[df["CPN_TYP"].isin(["FIXED"])]
    print(f"➡ Após filtrar CPN_TYP='FIXED': {len(df)}")

    df = df[df["CRNCY"].isin(["BRL"])]
    print(f"➡ Após filtrar CRNCY='BRL': {len(df)}")

    # 4. Normalizar INFLATION_LINKED_INDICATOR
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

    # 5. Validar covariável financeira
    df["TOT_DEBT_TO_EBITDA"] = pd.to_numeric(df["TOT_DEBT_TO_EBITDA"], errors="coerce")
    print(f"➡ Após conversão de TOT_DEBT_TO_EBITDA (com NaN): {df['TOT_DEBT_TO_EBITDA'].isna().sum()} NaNs")
    df = df[df["TOT_DEBT_TO_EBITDA"].notna()]
    print(f"➡ Após remover TOT_DEBT_TO_EBITDA nulos: {len(df)}")

    df["MATURITY"] = pd.to_datetime(df["MATURITY"], errors="coerce")
    return df


def anomaly_filtering_results(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica filtros-padrão para eliminar anomalias:
    - Yield igual a zero
    - Spreads muito extremos (> ±10 bps)
    """
    df = df.copy()
    df = df[df["YAS_BOND_YLD"] != 0]
    df = df[(df["SPREAD"] >= -10) & (df["SPREAD"] <= 10)]
    return df