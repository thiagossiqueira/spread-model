# tests/test_spread_calculator.py
import pytest
import pandas as pd
from core.spread_calculator import compute_spreads


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


def test_compute_spread_positive(mock_data):
    corp_base, yields_ts, yc_table, obs_win, tenors = mock_data
    result, skipped = compute_spreads(corp_base, yields_ts, yc_table, obs_win, tenors)

    assert not result.empty
    assert result["SPREAD"].iloc[0] > 0
    assert result["YAS_BOND_YLD"].iloc[0] > result["DI_YIELD"].iloc[0]
    assert skipped == []
