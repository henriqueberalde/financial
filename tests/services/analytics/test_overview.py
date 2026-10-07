from datetime import date

from financial.services.analytics import overview
from financial.services.analytics.overview import (ABOVE_AVERAGE, Alert,
                                                   UNCATEGORIZED_SHARE)
from financial.services.analytics.recurring import NEW

from factories import month


def test_overview_compares_the_month_with_the_trailing_average(add, load):
    add("2026-01-05", "SALARY", 1000)
    add("2026-01-06", "MARKET", -600, "Market", balance=900)
    add("2026-02-05", "SALARY", 1000, balance=1500)
    add("2026-02-06", "MARKET", -800, "Market", balance=700)
    add("2026-03-05", "SALARY", 2000, balance=2700)
    add("2026-03-06", "MARKET", -500, "Market", balance=2200)
    add("2026-03-07", "CARD SHOP", -500, "Gift", "Luxury", balance=None)
    add("2026-03-08", "APLICACAO CDB", -1000, balance=1200)

    result = overview.overview(load(), month("2026-03"))

    assert result.month == "2026-03"
    assert result.income == overview.Indicator(
        2000, 1000, [0] * 9 + [1000, 1000, 2000])
    assert (result.expense.value, result.expense.average) == (1000, 700)
    assert (result.result.value, result.result.average) == (1000, 300)
    assert (result.savings_rate.value, result.savings_rate.average) == \
        (0.5, 0.3)
    assert result.savings_rate.trend[0] is None
    assert result.flow[-1] == overview.MonthFlow("2026-03", 2000, 1000, 1000)
    assert len(result.flow) == 12
    assert [(s.sector, s.value, s.share) for s in result.sectors] == \
        [("Essential", 500, 0.5), ("Luxury", 500, 0.5)]
    assert result.balance[0] == overview.BalancePoint(date(2026, 1, 5), 1)
    assert result.balance[-1] == \
        overview.BalancePoint(date(2026, 3, 8), 1200)


def test_overview_without_history(add, load):
    add("2026-03-05", "SALARY", 100)

    result = overview.overview(load(), month("2026-03"))

    assert result.income.average is None
    assert result.sectors == []


def test_alerts(add, load):
    add("2025-06-05", "OLD", -10)
    for day in ("2025-12-05", "2026-01-05", "2026-02-05"):
        add(day, "MARKET", -200, "Market")
    add("2026-03-05", "MARKET", -500, "Market")
    add("2026-03-06", "BAR", -150, "Bar")
    for day in ("2026-01-10", "2026-02-10", "2026-03-10"):
        add(day, "STREAMING", -40, "Bills")
    add("2026-03-11", "UNKNOWN", -100)

    result = overview.alerts(load(), month("2026-03"))

    assert result == [
        Alert(ABOVE_AVERAGE, "Market", 500, 150),
        Alert(NEW, "STREAMING", 40, 40),
        Alert(UNCATEGORIZED_SHARE, "Sem categoria", 0.1266, 0.05),
    ]


def test_alerts_of_a_new_recurring_without_previous_value(add, load,
                                                          monkeypatch):
    monkeypatch.setattr(overview.recurring, "NEW_RECURRING_MONTHS", 1)
    add("2025-06-05", "OLD", -10)
    add("2026-03-10", "STREAMING", -40, "Bills")

    assert overview.alerts(load(), month("2026-03")) == \
        [Alert(NEW, "STREAMING", 40, None)]
