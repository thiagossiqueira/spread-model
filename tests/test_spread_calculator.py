# tests/test_spread_calculator.py

import pandas as pd
import pytest
from core.spread_calculator import compute_spreads
from calendars.daycounts import DayCounts

DAYCOUNT = DayCounts("bus/252", calendar="cdr_anbima")

def test_compute_spread_positive():
    # 1. Simula base de dados de 1 bond
    corp_base = pd.DataFrame({
        "id": ["BOND1"],                        # ← chave para ligar com yields_ts
        "generic_ticker_id": ["BOND1"],
        "MATURITY": [pd.Timestamp("2026-01-01")]
    })

    # 2. Simula yields observados para este bond
    index = pd.to_datetime(["2025-01-01", "2025-01-02", "2025-01-03"])
    yields_ts = pd.DataFrame({
        "BOND1": [12.5, 12.7, 12.9]
    }, index=index)

    # 3. Simula curva DI interpolada nas mesmas datas
    tenors_dict = {"1-year": 1.0, "2-year": 2.0}
    yc_table_data = []
    for date in index:
        yc_table_data.append({
            "obs_date": date,
            "1-year": 11.0 + 0.2 * (date.day - 1),
            "2-year": 11.5 + 0.2 * (date.day - 1),
        })
    yc_table = pd.DataFrame(yc_table_data).set_index("obs_date")

    # 4. Janela de observação fictícia
    obs_win = {
        "BOND1": (pd.Timestamp("2025-01-01"), pd.Timestamp("2025-01-03"))
    }

    # 5. Executa a função e valida
    result, skipped = compute_spreads(corp_base, yields_ts, yc_table, obs_win, tenors_dict)

    assert not result.empty
    assert skipped == []
    assert all(result["SPREAD"] > 0)