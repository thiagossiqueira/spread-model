# core/spread_calculator.py
import numpy as np
import pandas as pd
from utils.interpolation import interpolate_yield_for_tenor
from calendars.daycounts import DayCounts

DAYCOUNT = DayCounts("bus/252", calendar="cdr_anbima")

def compute_spreads(corp_base, yields_ts, yc_table, observation_periods, tenors_dict):
    expanded_rows = []
    skipped = []

    for _, bond in corp_base.iterrows():
        bond_id = bond["id"]
        obs_start, obs_end = observation_periods.get(bond_id, (None, None))
        if obs_start is None:
            continue

        for obs_date, di_row in yc_table.iterrows():
            if not (obs_start <= obs_date <= obs_end):
                continue

            try:
                yas_yld = yields_ts.at[obs_date, bond_id]
            except KeyError:
                skipped.append((bond_id, obs_date, "Missing column or date"))
                continue
            if pd.isna(yas_yld):
                skipped.append((bond_id, obs_date, "NaN yield"))
                continue

            tenor_yrs = DAYCOUNT.tf(obs_date, bond["MATURITY"])

            if tenor_yrs <= 0:
                continue

            interpolated_di_yield = interpolate_yield_for_tenor(
                obs_date, yc_table, tenor_yrs, tenors_dict, obs_date
            )

            spread = yas_yld - interpolated_di_yield

            expanded_rows.append({
                "id": bond_id,
                "OBS_DATE": obs_date,
                "MATURITY": bond["MATURITY"],
                "YAS_BOND_YLD": yas_yld,
                "DI_YIELD": interpolated_di_yield,
                "SPREAD": spread,
                "CPN_TYP": "Corp bond",
                "CPN": np.nan,
                "DAYS_TO_MATURITY": (bond["MATURITY"] - obs_date).days,
                "TENOR_YRS": tenor_yrs,
            })

    corp_bonds = pd.DataFrame(expanded_rows)
    if corp_bonds.empty:
        raise ValueError("No valid corporate bond spreads calculated.")

    names = list(tenors_dict.keys())
    vals = np.array(list(tenors_dict.values()))
    corp_bonds["TENOR_BUCKET"] = corp_bonds["TENOR_YRS"].apply(
        lambda y: names[np.argmin(np.abs(vals - y))]
    )

    return corp_bonds, skipped
