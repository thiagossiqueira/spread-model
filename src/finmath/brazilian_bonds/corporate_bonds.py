# corporate_bonds.py  –  Fixed-coupon / zero-coupon corporate bond (“Calc-Type 1”)

from __future__ import annotations

import warnings
from datetime import date
from typing import List, Optional

import pandas as pd
from dateutil.relativedelta import relativedelta
from scipy import optimize


# ─────────── ACT/ACT-ISDA year-fraction (Excel basis=1) ───────────
def _is_leap(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _yearfrac_act_act(start: date, end: date) -> float:
    """Exact ACT/ACT-ISDA, identical to Excel YEARFRAC(basis = 1)."""
    if start == end:
        return 0.0
    if start > end:
        start, end = end, start

    total, cur = 0.0, start
    while cur < end:
        nxt = date(cur.year + 1, 1, 1)
        seg_end = min(end, nxt)
        feb29 = date(cur.year, 2, 29) if _is_leap(cur.year) else None
        denom = 366 if feb29 and cur <= feb29 < seg_end else 365
        total += (seg_end - cur).days / denom
        cur = seg_end
    return total


# ─────────────────────── Bond class ───────────────────────────────
class CorpsCalcs1:
    """
    Spreadsheet-compatible bullet bond (Calc-Type 1).

    • Zero-coupon: set coupon_rate = 0.0
    • Fixed-coupon: any frequency (freq = coupons per year)
    • Discount style:
        – compound for zeros
        – simple-interest for coupon bonds (matches Bloomberg CONV A)
    """

    # ───────────── constructor ─────────────
    def __init__(
        self,
        *,
        expiry: "date | str",
        rate: Optional[float] = None,
        price: Optional[float] = None,
        principal: float = 100.0,
        coupon_rate: float = 0.05,
        freq: int = 1,
        ref_date: "date | str" = date.today(),
        first_coupon_date: Optional["date | str"] = None,
    ):
        if rate is None and price is None:
            raise ValueError("Either `rate` or `price` must be supplied.")

        self.expiry: date = pd.to_datetime(expiry).date()
        self.ref_date: date = pd.to_datetime(ref_date).date()
        self.principal: float = float(principal)
        self.coupon_rate: float = float(coupon_rate)
        self.freq: int = int(freq)
        self.first_coupon_date: Optional[date] = (
            pd.to_datetime(first_coupon_date).date() if first_coupon_date else None
        )

        self.cpn_amt: float = (self.coupon_rate / self.freq) * self.principal
        self.schedule: List[date] = self._build_schedule()
        self.coupon_at_expiry: bool = self._pays_coupon_at_expiry()

        # pricing inputs ----------------------------------------------------
        if rate is not None:
            self.rate: float = float(rate)
            self.price: float = self._clean_from_rate(self.rate)
        else:
            self.price: float = float(price)
            self.rate: float = self._rate_from_clean(self.price)

        # risk measures -----------------------------------------------------
        self.mod_duration, self.convexity = self._risk()
        self.macaulay: float = self.mod_duration * (1 + self.rate)
        self.dv01: float = self.mod_duration * self.price / 100

    # ───────────── helpers ─────────────
    def _build_schedule(self) -> List[date]:
        """Strictly ascending list of coupon dates (incl. maturity)."""
        anchor = self.first_coupon_date or self.expiry
        step = relativedelta(months=int(12 / self.freq))

        dates: List[date] = []
        d = anchor
        if d < self.expiry:
            while d < self.expiry:
                dates.append(d)
                d += step
        dates.append(self.expiry)  # ensure maturity appears once
        return dates

    def _pays_coupon_at_expiry(self) -> bool:
        if len(self.schedule) < 2:
            return False
        prev = self.schedule[-2]
        return abs(_yearfrac_act_act(prev, self.expiry) - 1 / self.freq) < 1e-4

    # discount factor ------------------------------------------------------
    def _df(self, y: float, t: float) -> float:
        if self.cpn_amt == 0.0:        # zero-coupon → compound
            return 1 / (1 + y) ** t
        return 1 / (1 + y * t)         # coupon bond → simple

    # ───────────── pricing ─────────────
    def _dirty_price(self, y: float) -> float:
        pv = 0.0
        for d in self.schedule:
            if d <= self.ref_date:
                continue
            cf = self.cpn_amt if (d != self.expiry or self.coupon_at_expiry) else 0.0
            if d == self.expiry:
                cf += self.principal
            t = _yearfrac_act_act(self.ref_date, d)
            pv += cf * self._df(y, t)
        return pv

    def _accrued(self) -> float:
        """
        Accrued interest on `ref_date`.

        Returns 0 when:
          • zero-coupon
          • ref_date ≥ maturity
          • ref_date before first coupon date
        """
        if self.cpn_amt == 0.0 or self.ref_date >= self.expiry:
            return 0.0
        if all(d > self.ref_date for d in self.schedule):
            return 0.0

        prev = max(d for d in self.schedule if d <= self.ref_date)
        next_ = min(d for d in self.schedule if d > self.ref_date)
        frac = _yearfrac_act_act(prev, self.ref_date) / _yearfrac_act_act(prev, next_)
        return frac * self.cpn_amt

    def _clean_from_rate(self, y: float) -> float:
        return self._dirty_price(y) - self._accrued()

    def _rate_from_clean(self, clean: float) -> float:
        target_dirty = clean + self._accrued()

        def f(yy: float) -> float:
            pv = 0.0
            for d in self.schedule:
                if d <= self.ref_date:
                    continue
                cf = self.cpn_amt if (d != self.expiry or self.coupon_at_expiry) else 0.0
                if d == self.expiry:
                    cf += self.principal
                t = _yearfrac_act_act(self.ref_date, d)
                pv += cf * self._df(yy, t)
            return pv - target_dirty

        return optimize.brentq(f, -0.95, 5.0)

    # ───────────── risk ─────────────
    def _risk(self) -> tuple[float, float]:
        mdur = conv = 0.0
        for d in self.schedule:
            if d <= self.ref_date:
                continue
            cf = self.cpn_amt if (d != self.expiry or self.coupon_at_expiry) else 0.0
            if d == self.expiry:
                cf += self.principal
            t = _yearfrac_act_act(self.ref_date, d)
            df = self._df(self.rate, t)
            pv = cf * df
            mdur += t * pv
            conv += t * (1 + t) * pv

        if self.price == 0.0:          # defensive guard
            warnings.warn("Zero clean price – duration/convexity set to 0")
            return 0.0, 0.0

        mdur /= self.price
        conv = (conv / self.price) / (1 + self.rate) ** 2
        return mdur, conv

    # ───────────── future cash-flows property ─────────────
    @property
    def cash_flows(self) -> pd.Series:
        """
        Future cash-flows (coupon + principal) strictly after `ref_date`,
        indexed by payment date.
        """
        vals, idx = [], []
        for d in self.schedule:
            if d <= self.ref_date:
                continue
            cf = self.cpn_amt if (d != self.expiry or self.coupon_at_expiry) else 0.0
            if d == self.expiry:
                cf += self.principal
            idx.append(d)
            vals.append(cf)
        return pd.Series(vals, index=idx)

    # ───────────── debug helper ─────────────
    def cashflow_table(self) -> pd.DataFrame:
        recs: list[dict] = []
        for d in self.schedule:
            cup = self.cpn_amt if (d != self.expiry or self.coupon_at_expiry) else 0.0
            prin = self.principal if d == self.expiry else 0.0
            cf = cup + prin
            yrs = _yearfrac_act_act(self.ref_date, d)
            df = 0.0 if yrs <= 0 else self._df(self.rate, yrs)
            pv = cf * df if yrs > 0 else 0.0
            recs.append(
                dict(
                    Date=d,
                    Coupon=cup,
                    Principal=prin,
                    DiscountPeriod=round(yrs, 9),
                    DF=round(df, 9),
                    PV=round(pv, 9),
                )
            )
        df = pd.DataFrame(recs)
        df.loc["Σ", "PV"] = df["PV"].sum()
        df.loc["Σ", ["Coupon", "Principal"]] = df[["Coupon", "Principal"]].sum()
        return df


# ───────────────────── quick sanity test ─────────────────────
if __name__ == "__main__":
    zc = CorpsCalcs1(
        expiry="2032-02-02",
        rate=0.12101044,
        coupon_rate=0.0,
        freq=1,
        principal=100,
        ref_date="2025-07-01",
    )
    print("Zero-coupon clean:", zc.price)

    bn = CorpsCalcs1(
        expiry="2026-01-22",
        rate=0.13382347,
        coupon_rate=0.05,
        freq=1,
        principal=100,
        ref_date="2025-07-01",
        first_coupon_date="2022-01-22",
    )
    print("Fixed-coupon clean:", bn.price)
    print("Future CFs ↓")
    print(bn.cash_flows)