from datetime import date

from financial.services.analytics import trends

from factories import month


def test_category_variance_compares_with_trailing_average(add, load):
    add("2026-01-10", "MARKET", -100, "Market")
    add("2026-02-10", "MARKET", -300, "Market")
    add("2026-02-11", "BAR", -50, "Bar", "Leisure")
    add("2026-03-10", "MARKET", -100, "Market")
    add("2026-03-11", "GYM", -90, "Gym")

    result = trends.category_variance(load(), month("2026-03"))

    assert [(v.category, v.value, v.average, v.difference, v.ratio)
            for v in result] == [
        ("Market", 100, 200, -100, -0.5),
        ("Gym", 90, 0, 90, None),
        ("Bar", 0, 25, -25, -1.0),
    ]
    assert result[2].sector == "Leisure"


def test_seasonality_averages_each_calendar_month(add, load):
    add("2025-01-10", "A", -100)
    add("2026-01-10", "B", -300)
    add("2026-02-10", "C", 10)

    result = trends.seasonality(load())

    assert [(s.month, s.average, s.samples) for s in result] == \
        [(1, 200, 2), (2, 0, 1)]


def test_largest_expenses_of_the_period(add, load):
    add("2026-01-10", "SMALL", -10)
    add("2026-01-11", "BIG", -900, "Travel")
    add("2026-01-12", "MEDIUM", -100)
    add("2026-05-12", "OUT OF PERIOD", -5000)

    result = trends.largest(load(), month("2026-01"), month("2026-03"), 2)

    assert [(e.description, e.amount, e.category) for e in result] == \
        [("BIG", 900, "Travel"), ("MEDIUM", 100, "Sem categoria")]
    assert result[0].date == date(2026, 1, 11)
