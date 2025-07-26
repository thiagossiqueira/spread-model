# core/windowing.py
import pandas as pd

def build_observation_windows(corp_base_df: pd.DataFrame, yields_ts: pd.DataFrame, window_days: int):
    window_length = pd.Timedelta(days=window_days)
    return {
        row["id"]: (
            max(yields_ts.index.min(), row["MATURITY"] - window_length),
            min(row["MATURITY"], yields_ts.index.max())
        )
        for _, row in corp_base_df.iterrows()
    }
