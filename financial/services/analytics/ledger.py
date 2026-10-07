import re

from typing import Literal

import pandas as pd

from sqlalchemy import select
from sqlalchemy.orm import Session

from financial.models.category import Category
from financial.models.transaction import Transaction
from financial.services.analytics.constants import (INVESTMENT_PATTERN,
                                                    TRAILING_MONTHS,
                                                    UNCATEGORIZED)

INCOME, EXPENSE, INVESTMENT = "income", "expense", "investment"
ACCOUNT, CARD = "account", "card"
Source = Literal["account", "card"]

COLUMNS = ["id", "date", "description", "value", "balance", "context",
           "category_id", "category", "sector"]


def load(session: Session) -> pd.DataFrame:
    """Every transaction with its category, classified by kind, month,
    merchant and source."""
    query = select(
        Transaction.id, Transaction.date, Transaction.description,
        Transaction.value, Transaction.balance, Transaction.context,
        Category.id, Category.name, Category.sector,
    ).outerjoin(Category, Category.id == Transaction.category_id) \
        .order_by(Transaction.date, Transaction.id)

    frame = pd.DataFrame(session.execute(query).all(), columns=COLUMNS)

    return classify(frame)


def classify(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.astype({"value": float, "balance": float})
    frame["date"] = pd.to_datetime(frame["date"])
    frame["month"] = frame["date"].dt.to_period("M")
    frame["category"] = frame["category"].fillna(UNCATEGORIZED)
    frame["sector"] = frame["sector"].fillna(UNCATEGORIZED)
    frame["category_id"] = frame["category_id"].astype("Int64")
    frame["kind"] = kind_of(frame)
    frame["merchant"] = frame["description"].map(merchant_name)
    # Credit card purchases do not change the account balance
    frame["source"] = frame["balance"].isna().map({True: CARD, False: ACCOUNT})

    return frame


def kind_of(frame: pd.DataFrame) -> pd.Series:
    investment = frame["description"].str.contains(
        INVESTMENT_PATTERN, case=False, regex=True)
    kind = pd.Series(EXPENSE, index=frame.index)
    kind[frame["value"] > 0] = INCOME
    kind[investment] = INVESTMENT

    return kind


def merchant_name(description: str) -> str:
    """Merchant or person name from a bank statement description."""
    # Installments of a purchase are charged by the same merchant
    name = re.sub(r"(?i)\s+-\s+parcela \d+/\d+$", "", description)
    if ":" in name[:30]:
        name = re.sub(r"^[^:]{0,30}:\s*", "", name)
    else:
        name = re.sub(r"^[^-]{0,30}-\s*", "", name)
    name = re.sub(r"(?i)(compra\s+)?no estabelecimento\s*", "", name)
    name = re.sub(r"(?i)^(cp\s*:\s*)?\d+-", "", name.strip('" '))
    name = re.sub(r"^[\d\s]+(?=[A-Za-z])", "", name)

    return re.sub(r"\s+", " ", name).strip('" ')[:40].strip()


def routine(frame: pd.DataFrame) -> pd.DataFrame:
    """Transactions out of trips and projects (no context)."""
    return frame[frame["context"].isna()]


def expenses(frame: pd.DataFrame) -> pd.DataFrame:
    """Routine expenses, with the spent amount as a positive number."""
    spent = routine(frame)
    spent = spent[(spent["kind"] == EXPENSE) & (spent["value"] < 0)]

    return spent.assign(amount=-spent["value"])


def incomes(frame: pd.DataFrame) -> pd.DataFrame:
    earned = routine(frame)

    return earned[earned["kind"] == INCOME]


def months_with_data(frame: pd.DataFrame) -> pd.PeriodIndex:
    return pd.PeriodIndex(sorted(frame["month"].unique()), freq="M")


def last_complete_month(frame: pd.DataFrame) -> pd.Period | None:
    """The last month with data whose last day was imported, or the first
    month with data when none is complete."""
    if frame.empty:
        return None

    last_day = frame["date"].max()
    complete = (last_day + pd.Timedelta(days=1)).to_period("M") - 1

    return max(complete, frame["month"].min())


def month_range(start: pd.Period, end: pd.Period) -> pd.PeriodIndex:
    return pd.period_range(start, end, freq="M")


def trailing_months(month: pd.Period,
                    count: int = TRAILING_MONTHS) -> pd.PeriodIndex:
    """The `count` months ending at `month`, inclusive."""
    return month_range(month - (count - 1), month)


def previous_months(month: pd.Period,
                    count: int = TRAILING_MONTHS) -> pd.PeriodIndex:
    """The `count` months right before `month`."""
    return month_range(month - count, month - 1)


def between(frame: pd.DataFrame,
            start: pd.Period,
            end: pd.Period) -> pd.DataFrame:
    return frame[(frame["month"] >= start) & (frame["month"] <= end)]


def monthly_totals(frame: pd.DataFrame,
                   column: str,
                   months: pd.PeriodIndex) -> pd.Series:
    return frame.groupby("month")[column].sum().reindex(months, fill_value=0.0)


def average_over_months_with_data(totals: pd.Series,
                                  with_data: pd.PeriodIndex) -> float:
    """Mean of the totals, ignoring months without any imported data, which
    would pull the average down."""
    present = totals[totals.index.isin(with_data)]

    return float(present.mean()) if len(present) > 0 else 0.0
