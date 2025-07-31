# tests/test_spread_calculator.py
import pandas as pd
from core.spread_calculator import compute_spreads
from calendars.daycounts import DayCounts
import pytest
DAYCOUNT = DayCounts("bus/252", calendar="cdr_anbima")


@pytest.fixture
def mock_data():
    corp_base = pd.DataFrame({
        "id": ["BOND1"],
        "MATURITY": [pd.Timestamp("2026-01-01")],
    })

    dates = pd.date_range("2025-01-01", periods=3)
    yields_ts = pd.DataFrame({"BOND1": [12.5, 12.7, 12.9]}, index=dates)

    yc_table = pd.DataFrame({
        "1-year": [11.0, 11.2, 11.4],
        "2-year": [11.5, 11.7, 11.9]
    }, index=dates)

    tenors_dict = {"1-year": 1.0, "2-year": 2.0}

    observation_periods = {"BOND1": (dates[0], dates[-1])}

    return corp_base, yields_ts, yc_table, observation_periods, tenors_dict


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

    # Define a curva DI para essas datas com curve_id como índice
    tenors_dict = {"1-year": 1.0, "2-year": 2.0}
    yc_table_data = []
    for date in index:
        curve_id = f"BOND1{date.strftime('%Y%m%d')}"
        yc_table_data.append({
            "curve_id": curve_id,
            "1-year": 11.0 + 0.2 * (date.day - 1),  # valores fictícios
            "2-year": 11.5 + 0.2 * (date.day - 1)
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
