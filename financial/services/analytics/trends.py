from dataclasses import dataclass
from datetime import date

import pandas as pd

from financial.services.analytics import ledger
from financial.services.analytics.constants import TOP_ITEMS


@dataclass(frozen=True)
class CategoryVariance:
    category: str
    sector: str
    value: float
    average: float
    difference: float
    # None when the category has no history to compare with
    ratio: float | None


@dataclass(frozen=True)
class SeasonalMonth:
    month: int
    average: float
    samples: int


@dataclass(frozen=True)
class LargeExpense:
    id: int
    date: date
    description: str
    category: str
    amount: float


def category_variance(frame: pd.DataFrame,
                      month: pd.Period) -> list[CategoryVariance]:
    """Expenses of each category in the month against its average in the
    trailing months with data, largest differences first."""
    spent = ledger.expenses(frame)
    previous = ledger.previous_months(month)
    with_data = ledger.months_with_data(frame)
    reference = previous[previous.isin(with_data)]

    current = spent[spent["month"] == month] \
        .groupby("category")["amount"].sum()
    history = spent[spent["month"].isin(reference)] \
        .groupby("category")["amount"].sum() / max(len(reference), 1)
    sectors = spent.groupby("category")["sector"].first()

    result = []
    for category in current.index.union(history.index):
        value = float(current.get(category, 0.0))
        average = float(history.get(category, 0.0))
        result.append(CategoryVariance(
            str(category), str(sectors[category]), round(value, 2),
            round(average, 2), round(value - average, 2),
            round(value / average - 1, 4) if average > 0 else None))

    return sorted(result, key=lambda item: -abs(item.difference))


def seasonality(frame: pd.DataFrame) -> list[SeasonalMonth]:
    """Average expenses per calendar month, over the months with data."""
    with_data = ledger.months_with_data(frame)
    totals = ledger.monthly_totals(ledger.expenses(frame), "amount",
                                   with_data)
    grouped = totals.groupby(totals.index.month)

    return [SeasonalMonth(int(month), round(float(values.mean()), 2),
                          len(values))
            for month, values in grouped]


def largest(frame: pd.DataFrame,
            start: pd.Period,
            end: pd.Period,
            limit: int = TOP_ITEMS) -> list[LargeExpense]:
    spent = ledger.between(ledger.expenses(frame), start, end) \
        .nlargest(limit, "amount")

    return [LargeExpense(int(row.id), row.date.date(), row.description,
                         row.category, round(row.amount, 2))
            for row in spent.itertuples()]
