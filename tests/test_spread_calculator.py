# tests/test_spread_calculator.py

import pandas as pd
from core.spread_calculator import compute_spreads
from calendars.daycounts import DayCounts
import pytest

DAYCOUNT = DayCounts("bus/252", calendar="cdr_anbima")

def test_compute_spread_positive():
    # Simula base de dados de 1 bond
    corp_base = pd.DataFrame({
        "id": ["BOND1"],
        "MATURITY": [pd.Timestamp("2026-01-01")]
    })

    # Simula yields observados para este bond
    index = pd.to_datetime(["2025-01-01", "2025-01-02", "2025-01-03"])
    yields_ts = pd.DataFrame({
        "BOND1": [12.5, 12.7, 12.9]
    }, index=index)

    # Define a curva DI para essas datas com generic_ticker_id + obs_date
    tenors_dict = {"1-year": 1.0, "2-year": 2.0}
    yc_table_data = []
    for date in index:
        curve_id = f"BOND1{date.strftime('%Y%m%d')}"
        yc_table_data.append({
            "curve_id": curve_id,
            "1-year": 11.0 + 0.2 * (date.day - 1),
            "2-year": 11.5 + 0.2 * (date.day - 1),
            "obs_date": date
        })

    yc_table = pd.DataFrame(yc_table_data).set_index("curve_id")

    # Janela de observação fictícia
    obs_win = {
        "BOND1": (pd.Timestamp("2025-01-01"), pd.Timestamp("2025-01-03"))
    }

    result, skipped = compute_spreads(corp_base, yields_ts, yc_table, obs_win, tenors_dict)

    assert not result.empty
    assert skipped == []
    assert all(result["SPREAD"] > 0)
