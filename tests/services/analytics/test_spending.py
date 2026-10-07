from datetime import date

from financial.services.analytics import spending
from financial.services.analytics.spending import SpendingFilter
from financial.services.analytics.ledger import CARD

from factories import month

YEAR = SpendingFilter(month("2026-01"), month("2026-12"))


def add_expenses(add):
    add("2026-01-10", "MARKET A", -100, "Market")
    add("2026-01-12", "MARKET B", -50, "Market")
    add("2026-02-03", "STEAKHOUSE", -80, "Restaurant", "Leisure")
    add("2026-02-05", "UNKNOWN SHOP", -20, balance=None)
    add("2026-02-06", "SALARY", 1000)
    add("2025-12-30", "OLD MARKET", -500, "Market")


def test_filter_slices_the_period_and_drill(add, load):
    add_expenses(add)
    frame = load()

    market = SpendingFilter(month("2026-01"), month("2026-12"),
                            sector="Essential", category="Market",
                            merchant="MARKET A")
    card = SpendingFilter(month("2026-01"), month("2026-12"), source=CARD)

    assert market.apply(frame)["amount"].tolist() == [100]
    assert card.apply(frame)["description"].tolist() == ["UNKNOWN SHOP"]


def test_tree_groups_sector_category_and_merchant(add, load):
    add_expenses(add)

    nodes = spending.tree(load(), YEAR)

    assert [(n.name, n.value) for n in nodes] == \
        [("Essential", 150), ("Leisure", 80), ("Sem categoria", 20)]
    market = nodes[0].children[0]
    assert (market.name, market.value) == ("Market", 150)
    assert [(n.name, n.value) for n in market.children] == \
        [("MARKET A", 100), ("MARKET B", 50)]


def test_tree_sums_up_the_smaller_merchants(add, load, monkeypatch):
    monkeypatch.setattr(spending, "TREE_MERCHANTS_PER_CATEGORY", 1)
    add_expenses(add)

    market = spending.tree(load(), YEAR)[0].children[0]

    assert [(n.name, n.value, n.other) for n in market.children] == \
        [("MARKET A", 100, False), ("+1", 50, True)]


def test_monthly_timeline_averages_months_with_data(add, load):
    add_expenses(add)
    quarter = SpendingFilter(month("2026-01"), month("2026-03"))

    result = spending.timeline(load(), quarter, "month")

    assert [(p.period, p.value) for p in result.points] == \
        [("2026-01", 150), ("2026-02", 100), ("2026-03", 0)]
    assert result.average == 125


def test_yearly_and_daily_timelines(add, load):
    add_expenses(add)
    january = SpendingFilter(month("2026-01"), month("2026-01"))

    years = spending.timeline(load(), YEAR, "year")
    days = spending.timeline(load(), january, "day")

    assert [(p.period, p.value) for p in years.points] == [("2026", 250)]
    assert len(days.points) == 31
    assert days.points[9].value == 100
    assert days.average == round(150 / 31, 2)


def test_merchants_ranks_by_total(add, load):
    add_expenses(add)
    add("2026-03-01", "MARKET B", -60, "Market")

    result = spending.merchants(load(), YEAR, limit=2)

    assert [(m.name, m.count, m.total) for m in result] == \
        [("MARKET B", 2, 110), ("MARKET A", 1, 100)]


def test_transactions_are_searched_and_paged(add, load):
    add_expenses(add)

    page = spending.transactions(load(), YEAR, search="market",
                                 limit=1, offset=1)
    everything = spending.transactions(load(), YEAR)

    assert (page.total, page.amount) == (2, 150)
    assert [(t.description, t.date) for t in page.items] == \
        [("MARKET A", date(2026, 1, 10))]
    assert page.items[0].category == "Market"
    assert everything.items[0].category_id is None
    assert everything.total == 4
