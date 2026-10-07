from datetime import date

from sqlalchemy.orm import Session

from financial.models.category import Category
from financial.models.category_rule import CategoryRule
from financial.services import categorization
from financial.services.analytics import categorization_quality as quality

from factories import month


def test_categorization_quality(session: Session, add, load):
    market = Category(name="Market", sector="Essential")
    water = Category(name="Water", sector="Essential")
    session.add_all([
        CategoryRule(category=market, rule="mercado"),
        CategoryRule(category=water, rule="agua"),
        CategoryRule(category=water, rule="never matches"),
    ])
    session.commit()
    add("2025-03-10", "OLD SHOP", -100)
    add("2026-01-10", "MERCADO SOL", -300)
    add("2026-01-11", "PIX ENVIADO - JOHN", -50)
    add("2026-02-11", "PIX ENVIADO - JOHN", -30)
    add("2026-02-12", "MERCADO AGUA", -20)
    picked = add("2026-02-13", "LOJA", -100)
    categorization.reprocess_categories(session)
    categorization.set_user_category(session, picked.id, market.id)

    result = quality.categorization_quality(session, load(), month("2026-12"))

    assert (result.start, result.end) == ("2026-01", "2026-12")
    assert result.target == 0.05
    assert (result.share, result.uncategorized_count) == (0.2, 3)
    assert [(y.year, y.expenses, y.uncategorized, y.share)
            for y in result.by_year] == [(2025, 100, 100, 1.0),
                                         (2026, 500, 100, 0.2)]
    assert result.methods == quality.CategorizationMethods(100, 300, 100)
    assert [(m.merchant, m.count, m.total, m.last_date, m.example)
            for m in result.merchants] == [
        ("JOHN", 2, 80, date(2026, 2, 11), "PIX ENVIADO - JOHN"),
        ("MERCADO AGUA", 1, 20, date(2026, 2, 12), "MERCADO AGUA"),
    ]
    assert [(c.description, c.categories, c.count)
            for c in result.conflicts] == \
        [("MERCADO AGUA", ["Market", "Water"], 1)]
    assert [(r.rule, r.category) for r in result.unused_rules] == \
        [("never matches", "Water")]


def test_categorization_quality_without_expenses(session: Session, load):
    result = quality.categorization_quality(session, load(), month("2026-12"))

    assert (result.share, result.by_year, result.merchants) == (0, [], [])
