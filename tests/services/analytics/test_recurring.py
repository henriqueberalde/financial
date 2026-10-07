import pandas as pd

from financial.services.analytics import recurring
from financial.services.analytics.recurring import NEW, PRICE_INCREASE

from factories import month

END = month("2026-12")


def add_monthly(add, description: str, values: list[float],
                category: str = "Bills") -> None:
    """Charge each value (negative for income) on the 5th, the last value in
    December 2026."""
    months = pd.period_range(end=END, periods=len(values), freq="M")
    for period, value in zip(months, values):
        if value:
            add(f"{period}-05", description, -value, category)


def test_recurring_needs_most_of_the_trailing_months(add, load):
    add_monthly(add, "RENT", [1000] * 12)
    add_monthly(add, "GYM", [100, 0, 100, 0, 100, 0, 100, 0, 100, 0, 100, 0])
    add_monthly(add, "CINEMA", [50, 0, 0, 0, 0, 50, 0, 0, 0, 0, 0, 0])
    add_monthly(add, "SALARY", [-4000] * 12)

    result = recurring.recurring(load(), END)

    assert [(i.merchant, i.months, i.average, i.last, i.status)
            for i in result.items] == [
        ("RENT", 12, 1000, 1000, None),
        ("GYM", 6, 100, 0, None),
    ]
    assert result.items[0].category == "Bills"
    assert result.items[1].monthly[:2] == [100, 0]
    assert result.months[0] == "2026-01"
    assert result.monthly_cost == 1100
    assert result.income_share == 0.275


def test_recurring_flags_new_and_price_increases(add, load):
    add_monthly(add, "STREAMING", [0] * 9 + [40, 40, 40])
    add_monthly(add, "PHONE", [70] * 11 + [80])
    add_monthly(add, "POWER", [100, 200, 120, 300, 90, 150, 220, 100, 180,
                               90, 140, 260])

    items = {item.merchant: item.status
             for item in recurring.recurring(load(), END).items}

    assert items == {"STREAMING": NEW, "PHONE": PRICE_INCREASE,
                     "POWER": None}


def test_recurring_is_not_new_when_the_data_starts_recently(add, load):
    add_monthly(add, "STREAMING", [0] * 9 + [40, 40, 40])

    assert recurring.recurring(load(), END).items == []


def test_recurring_without_income(add, load):
    add_monthly(add, "RENT", [1000] * 12)

    assert recurring.recurring(load(), END).income_share is None
