import re

from dataclasses import dataclass
from datetime import date

import pandas as pd

from sqlalchemy.orm import Session

from financial.models.category_rule import CategoryRule
from financial.models.transaction_category import TransactionCategory
from financial.services.analytics import ledger
from financial.services.analytics.constants import (TOP_ITEMS,
                                                    UNCATEGORIZED,
                                                    UNCATEGORIZED_TARGET)
from financial.services.categorization import (CategoryRuleConflictError,
                                               category_id_for)


@dataclass(frozen=True)
class YearShare:
    year: int
    expenses: float
    uncategorized: float
    share: float


@dataclass(frozen=True)
class CategorizationMethods:
    """Expenses by how they got their category."""
    by_user: float
    by_rule: float
    uncategorized: float


@dataclass(frozen=True)
class UncategorizedMerchant:
    merchant: str
    count: int
    total: float
    last_date: date
    example: str


@dataclass(frozen=True)
class RuleConflict:
    description: str
    categories: list[str]
    count: int


@dataclass(frozen=True)
class UnusedRule:
    id: int
    rule: str
    category: str


@dataclass(frozen=True)
class CategorizationQuality:
    start: str
    end: str
    target: float
    share: float
    uncategorized_count: int
    by_year: list[YearShare]
    methods: CategorizationMethods
    merchants: list[UncategorizedMerchant]
    conflicts: list[RuleConflict]
    unused_rules: list[UnusedRule]


def categorization_quality(session: Session,
                           frame: pd.DataFrame,
                           end: pd.Period) -> CategorizationQuality:
    """How well the expenses of the trailing months ending at `end` are
    categorized, and what to fix next."""
    window = ledger.trailing_months(end)
    spent = ledger.expenses(frame)
    recent = ledger.between(spent, window[0], end)
    missing = recent[recent["category"] == UNCATEGORIZED]
    rules = session.query(CategoryRule).all()
    descriptions = frame["description"].value_counts()

    return CategorizationQuality(
        str(window[0]), str(end), UNCATEGORIZED_TARGET,
        uncategorized_share(recent),
        len(missing), by_year(spent), methods(session, recent),
        uncategorized_merchants(missing),
        conflicts(descriptions, rules), unused_rules(descriptions, rules))


def uncategorized_share(spent: pd.DataFrame) -> float:
    """Share of the expenses amount without category."""
    missing = spent.loc[spent["category"] == UNCATEGORIZED, "amount"].sum()

    return _share(missing, spent["amount"].sum())


def by_year(spent: pd.DataFrame) -> list[YearShare]:
    years = spent.assign(missing=spent["amount"].where(
        spent["category"] == UNCATEGORIZED, 0.0)) \
        .groupby(spent["date"].dt.year)[["amount", "missing"]].sum()

    return [YearShare(int(year), round(row["amount"], 2),
                      round(row["missing"], 2),
                      _share(row["missing"], row["amount"]))
            for year, row in years.iterrows()]


def methods(session: Session, spent: pd.DataFrame) -> CategorizationMethods:
    chosen = {row.transaction_id
              for row in session.query(TransactionCategory.transaction_id)}
    missing = spent["category"] == UNCATEGORIZED
    by_user = spent["id"].isin(chosen) & ~missing

    return CategorizationMethods(
        round(float(spent.loc[by_user, "amount"].sum()), 2),
        round(float(spent.loc[~by_user & ~missing, "amount"].sum()), 2),
        round(float(spent.loc[missing, "amount"].sum()), 2))


def uncategorized_merchants(
        missing: pd.DataFrame,
        limit: int = TOP_ITEMS) -> list[UncategorizedMerchant]:
    grouped = missing.sort_values("date").groupby("merchant").agg(
        count=("amount", "size"), total=("amount", "sum"),
        last_date=("date", "max"), example=("description", "last"),
    ).nlargest(limit, "total")

    return [UncategorizedMerchant(str(merchant), int(row["count"]),
                                  round(row["total"], 2),
                                  row["last_date"].date(), row["example"])
            for merchant, row in grouped.iterrows()]


def conflicts(descriptions: pd.Series,
              rules: list[CategoryRule]) -> list[RuleConflict]:
    """Descriptions matched by rules of more than one category, which are
    left uncategorized."""
    result = []
    for description, count in descriptions.items():
        try:
            category_id_for(str(description), rules)
        except CategoryRuleConflictError as e:
            categories = sorted({rule.category.name
                                 for rule in e.conflicted_category_rules})
            result.append(RuleConflict(str(description), categories,
                                       int(count)))

    return sorted(result, key=lambda conflict: -conflict.count)


def unused_rules(descriptions: pd.Series,
                 rules: list[CategoryRule]) -> list[UnusedRule]:
    """Rules that match no transaction."""
    texts = [str(description) for description in descriptions.index]

    return [UnusedRule(int(rule.id), str(rule.rule), rule.category.name)
            for rule in rules
            if not any(re.search(str(rule.rule), text, re.IGNORECASE)
                       for text in texts)]


def _share(part: float, whole: float) -> float:
    return round(float(part / whole), 4) if whole > 0 else 0.0
