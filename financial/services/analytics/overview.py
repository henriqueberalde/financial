from dataclasses import dataclass
from datetime import date

import pandas as pd

from financial.services.analytics import ledger, recurring, trends
from financial.services.analytics.constants import (ABOVE_AVERAGE_MIN_RATIO,
                                                    ABOVE_AVERAGE_MIN_VALUE,
                                                    UNCATEGORIZED,
                                                    UNCATEGORIZED_TARGET)

ABOVE_AVERAGE = "above_average"
UNCATEGORIZED_SHARE = "uncategorized_share"


@dataclass(frozen=True)
class Indicator:
    value: float | None
    # Mean of the trailing months with data, before the month
    average: float | None
    # Values of the trailing months, ending at the month
    trend: list[float | None]


@dataclass(frozen=True)
class MonthFlow:
    month: str
    income: float
    expense: float
    result: float


@dataclass(frozen=True)
class SectorTotal:
    sector: str
    value: float
    share: float


@dataclass(frozen=True)
class BalancePoint:
    date: date
    balance: float


@dataclass(frozen=True)
class Alert:
    kind: str
    subject: str
    value: float
    reference: float | None


@dataclass(frozen=True)
class Overview:
    month: str
    income: Indicator
    expense: Indicator
    result: Indicator
    savings_rate: Indicator
    flow: list[MonthFlow]
    sectors: list[SectorTotal]
    balance: list[BalancePoint]
    alerts: list[Alert]


def overview(frame: pd.DataFrame, month: pd.Period) -> Overview:
    window = ledger.trailing_months(month)
    flow = monthly_flow(frame, ledger.month_range(window[0] - 1, month))
    reference = flow.loc[ledger.previous_months(month)]
    reference = reference[reference.index.isin(
        ledger.months_with_data(frame))]
    shown = flow.loc[window]

    return Overview(
        str(month),
        *[_indicator(shown[column], reference[column])
          for column in ("income", "expense", "result", "savings_rate")],
        [MonthFlow(str(period), round(row.income, 2), round(row.expense, 2),
                   round(row.result, 2))
         for period, row in shown.iterrows()],
        sectors(frame, month), balance(frame, window[0], month),
        alerts(frame, month))


def monthly_flow(frame: pd.DataFrame,
                 months: pd.PeriodIndex) -> pd.DataFrame:
    """Routine income, expense, result and savings rate of each month.
    Investments are neither income nor expense."""
    flow = pd.DataFrame({
        "income": ledger.monthly_totals(ledger.incomes(frame), "value",
                                        months),
        "expense": ledger.monthly_totals(ledger.expenses(frame), "amount",
                                         months),
    })
    flow["result"] = flow["income"] - flow["expense"]
    flow["savings_rate"] = (flow["result"] / flow["income"]) \
        .where(flow["income"] > 0)

    return flow


def sectors(frame: pd.DataFrame, month: pd.Period) -> list[SectorTotal]:
    spent = ledger.expenses(frame)
    totals = spent[spent["month"] == month].groupby("sector")["amount"] \
        .sum().sort_values(ascending=False)
    total = totals.sum()

    return [SectorTotal(str(sector), round(float(value), 2),
                        round(float(value / total), 4))
            for sector, value in totals.items()]


def balance(frame: pd.DataFrame,
            start: pd.Period,
            end: pd.Period) -> list[BalancePoint]:
    """Account balance at the end of each day with transactions."""
    days = ledger.between(frame, start, end).dropna(subset=["balance"]) \
        .groupby(frame["date"].dt.date)["balance"].last()

    return [BalancePoint(day, round(float(value), 2))
            for day, value in days.items()]


def alerts(frame: pd.DataFrame, month: pd.Period) -> list[Alert]:
    """What deserves attention in the month: categories above their
    average, new recurring expenses, price increases and uncategorized
    expenses above the target."""
    result = [
        Alert(ABOVE_AVERAGE, item.category, item.value, item.average)
        for item in trends.category_variance(frame, month)
        if item.category != UNCATEGORIZED and item.ratio is not None
        and item.ratio >= ABOVE_AVERAGE_MIN_RATIO
        and item.difference >= ABOVE_AVERAGE_MIN_VALUE
    ]
    result += [
        Alert(str(item.status), item.merchant, item.last,
              _usual_value(item))
        for item in recurring.recurring(frame, month).items
        if item.status is not None
    ]

    share = _uncategorized_share(frame, month)
    if share > UNCATEGORIZED_TARGET:
        result.append(Alert(UNCATEGORIZED_SHARE, UNCATEGORIZED, share,
                            UNCATEGORIZED_TARGET))

    return result


def _indicator(values: pd.Series, reference: pd.Series) -> Indicator:
    reference = reference.dropna()

    return Indicator(
        _rounded(values.iloc[-1]),
        _rounded(reference.mean()) if len(reference) > 0 else None,
        [_rounded(value) for value in values])


def _rounded(value: float) -> float | None:
    return None if pd.isna(value) else round(float(value), 4)


def _usual_value(item: recurring.RecurringExpense) -> float | None:
    before = [value for value in item.monthly[:-1] if value > 0]

    return round(float(pd.Series(before).median()), 2) if before else None


def _uncategorized_share(frame: pd.DataFrame, month: pd.Period) -> float:
    spent = ledger.expenses(frame)
    spent = spent[spent["month"] == month]
    total = spent["amount"].sum()
    missing = spent.loc[spent["category"] == UNCATEGORIZED, "amount"].sum()

    return round(float(missing / total), 4) if total > 0 else 0.0
