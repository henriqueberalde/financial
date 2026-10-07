from dataclasses import dataclass

import pandas as pd

from financial.services.analytics import ledger
from financial.services.analytics.constants import (
    NEW_RECURRING_MONTHS, PRICE_INCREASE_MIN_RATIO, RECURRING_MIN_MONTHS,
    STABLE_VALUE_MAX_VARIATION)

NEW, PRICE_INCREASE = "new", "price_increase"


@dataclass(frozen=True)
class RecurringExpense:
    merchant: str
    category: str
    months: int
    # Total of each trailing month, oldest first
    monthly: list[float]
    average: float
    last: float
    status: str | None


@dataclass(frozen=True)
class RecurringExpenses:
    months: list[str]
    monthly_cost: float
    # Share of the average income; None without income
    income_share: float | None
    items: list[RecurringExpense]


def recurring(frame: pd.DataFrame, end: pd.Period) -> RecurringExpenses:
    """Merchants charged in most of the trailing months ending at `end`,
    plus the ones charged in every recent month only."""
    window = ledger.trailing_months(end)
    spent = ledger.between(ledger.expenses(frame), window[0], end)
    totals = spent.pivot_table(index="merchant", columns="month",
                               values="amount", aggfunc="sum") \
        .reindex(columns=window).fillna(0.0)
    categories = spent.groupby("merchant")["category"] \
        .agg(lambda values: values.mode().iloc[0])

    items = [_expense(str(merchant), str(categories[merchant]), monthly)
             for merchant, monthly in totals.iterrows()]
    items = sorted([item for item in items if item is not None],
                   key=lambda item: -item.average)

    monthly_cost = round(sum(item.average for item in items), 2)

    return RecurringExpenses([str(month) for month in window], monthly_cost,
                             _income_share(frame, window, monthly_cost),
                             items)


def _expense(merchant: str,
             category: str,
             monthly: pd.Series) -> RecurringExpense | None:
    present = monthly[monthly > 0]
    recent = monthly.iloc[-NEW_RECURRING_MONTHS:]
    earlier = monthly.iloc[:-NEW_RECURRING_MONTHS]
    is_new = bool((recent > 0).all() and (earlier == 0).all())

    if len(present) < RECURRING_MIN_MONTHS and not is_new:
        return None

    status = NEW if is_new else (
        PRICE_INCREASE if _price_increased(monthly, present) else None)

    return RecurringExpense(
        merchant, category, len(present),
        [round(float(value), 2) for value in monthly],
        round(float(present.mean()), 2), round(float(monthly.iloc[-1]), 2),
        status)


def _price_increased(monthly: pd.Series, present: pd.Series) -> bool:
    """A stable value until the month before, charged higher in the last."""
    if monthly.iloc[-1] == 0:
        return False

    before = present.iloc[:-1]
    usual = before.median()
    variation = before.std(ddof=0) / before.mean()

    return bool(variation <= STABLE_VALUE_MAX_VARIATION and
                monthly.iloc[-1] > usual * (1 + PRICE_INCREASE_MIN_RATIO))


def _income_share(frame: pd.DataFrame,
                  window: pd.PeriodIndex,
                  monthly_cost: float) -> float | None:
    income = ledger.average_over_months_with_data(
        ledger.monthly_totals(ledger.incomes(frame), "value", window),
        ledger.months_with_data(frame))

    return round(monthly_cost / income, 4) if income > 0 else None
