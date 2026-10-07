from dataclasses import dataclass, field
from datetime import date
from typing import Literal

import pandas as pd

from financial.services.analytics import ledger
from financial.services.analytics.constants import (
    PAGE_SIZE, TOP_ITEMS, TREE_MERCHANTS_PER_CATEGORY)

Granularity = Literal["year", "month", "day"]


@dataclass(frozen=True)
class SpendingFilter:
    """Slice of the routine expenses the spending page is looking at."""
    start: pd.Period
    end: pd.Period
    sector: str | None = None
    category: str | None = None
    merchant: str | None = None
    source: str | None = None

    def period(self, frame: pd.DataFrame) -> pd.DataFrame:
        spent = ledger.between(ledger.expenses(frame), self.start, self.end)
        if self.source is not None:
            spent = spent[spent["source"] == self.source]

        return spent

    def apply(self, frame: pd.DataFrame) -> pd.DataFrame:
        spent = self.period(frame)
        for column in ("sector", "category", "merchant"):
            value = getattr(self, column)
            if value is not None:
                spent = spent[spent[column] == value]

        return spent


@dataclass(frozen=True)
class TreeNode:
    name: str
    value: float
    children: list["TreeNode"] = field(default_factory=list)
    # Sum of the smaller merchants of a category, not a merchant itself
    other: bool = False


@dataclass(frozen=True)
class TimelinePoint:
    period: str
    value: float


@dataclass(frozen=True)
class Timeline:
    granularity: Granularity
    points: list[TimelinePoint]
    average: float


@dataclass(frozen=True)
class MerchantTotal:
    name: str
    count: int
    total: float


@dataclass(frozen=True)
class TransactionRow:
    id: int
    date: date
    description: str
    merchant: str
    source: str
    category_id: int | None
    category: str
    sector: str
    amount: float


@dataclass(frozen=True)
class TransactionPage:
    total: int
    amount: float
    items: list[TransactionRow]


def tree(frame: pd.DataFrame, spending: SpendingFilter) -> list[TreeNode]:
    """Expenses of the period as sector > category > merchant, ignoring the
    drill filters so every branch stays reachable."""
    spent = spending.period(frame)

    return [
        TreeNode(str(sector), _sum(by_sector), [
            TreeNode(str(category), _sum(by_category),
                     _merchant_nodes(by_category))
            for category, by_category in _largest_groups(by_sector,
                                                         "category")
        ])
        for sector, by_sector in _largest_groups(spent, "sector")
    ]


def timeline(frame: pd.DataFrame,
             spending: SpendingFilter,
             granularity: Granularity) -> Timeline:
    spent = spending.apply(frame)

    if granularity == "month":
        months = ledger.month_range(spending.start, spending.end)
        totals = ledger.monthly_totals(spent, "amount", months)
        average = ledger.average_over_months_with_data(
            totals, ledger.months_with_data(frame))
    else:
        totals = _totals_by(spent, spending, granularity)
        average = float(totals.mean())

    points = [TimelinePoint(str(period), round(float(value), 2))
              for period, value in totals.items()]

    return Timeline(granularity, points, round(average, 2))


def merchants(frame: pd.DataFrame,
              spending: SpendingFilter,
              limit: int = TOP_ITEMS) -> list[MerchantTotal]:
    grouped = spending.apply(frame).groupby("merchant")["amount"] \
        .agg(["count", "sum"]).nlargest(limit, "sum")

    return [MerchantTotal(str(name), int(row["count"]), round(row["sum"], 2))
            for name, row in grouped.iterrows()]


def transactions(frame: pd.DataFrame,
                 spending: SpendingFilter,
                 search: str | None = None,
                 limit: int = PAGE_SIZE,
                 offset: int = 0) -> TransactionPage:
    spent = spending.apply(frame)
    if search:
        spent = spent[spent["description"].str.contains(
            search, case=False, regex=False)]

    page = spent.sort_values(["date", "id"], ascending=False) \
        .iloc[offset:offset + limit]

    return TransactionPage(len(spent), _sum(spent), [
        TransactionRow(
            int(row.id), row.date.date(), row.description, row.merchant,
            row.source,
            None if pd.isna(row.category_id) else int(row.category_id),
            row.category, row.sector, round(row.amount, 2))
        for row in page.itertuples()
    ])


def _sum(frame: pd.DataFrame) -> float:
    return round(float(frame["amount"].sum()), 2)


def _largest_groups(frame: pd.DataFrame, column: str):
    groups = list(frame.groupby(column))

    return sorted(groups, key=lambda group: -group[1]["amount"].sum())


def _merchant_nodes(frame: pd.DataFrame) -> list[TreeNode]:
    totals = frame.groupby("merchant")["amount"].sum() \
        .sort_values(ascending=False)
    nodes = [TreeNode(str(name), round(float(value), 2))
             for name, value in
             totals.iloc[:TREE_MERCHANTS_PER_CATEGORY].items()]

    rest = totals.iloc[TREE_MERCHANTS_PER_CATEGORY:]
    if len(rest) > 0:
        nodes.append(TreeNode(f"+{len(rest)}", round(float(rest.sum()), 2),
                              other=True))

    return nodes


def _totals_by(spent: pd.DataFrame,
               spending: SpendingFilter,
               granularity: Granularity) -> pd.Series:
    first_day = spending.start.start_time
    last_day = spending.end.end_time.normalize()

    if granularity == "year":
        index = pd.period_range(first_day, last_day, freq="Y")
        keys = spent["date"].dt.to_period("Y")
    else:
        index = pd.period_range(first_day, last_day, freq="D")
        keys = spent["date"].dt.to_period("D")

    return spent.groupby(keys)["amount"].sum().reindex(index, fill_value=0.0)
