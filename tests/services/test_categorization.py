from sqlalchemy.orm import Session

from factories import make_transaction
from financial.models.category import Category
from financial.models.category_rule import CategoryRule
from financial.models.transaction import Transaction
from financial.models.transaction_category import TransactionCategory
from financial.services import categorization
from financial.services.categorization import CategoryRuleConflictError


def test_set_categories_by_rules(session: Session):
    category1, category2 = __add_categories_with_rules(session)
    t1 = make_transaction("PAGAMENTO DE CONVENIO - category1")
    t2 = make_transaction("PAGAMENTO DE CONVENIO - category2")
    t3 = make_transaction("PAGAMENTO DE CONVENIO - Nao categorizado")
    session.add_all([t1, t2, t3])
    session.commit()

    categorization.set_categories_by_rules(session,
                                           session.query(CategoryRule).all())

    assert t1.category_id == category1.id
    assert t2.category_id == category2.id
    assert t3.category_id is None


def test_set_categories_by_rules_skips_conflicts(session: Session):
    category1, _ = __add_categories_with_rules(session)
    conflicting = make_transaction("category1 category2")
    single_match = make_transaction("only category1")
    session.add_all([conflicting, single_match])
    session.commit()

    errors = categorization.set_categories_by_rules(
        session, session.query(CategoryRule).all())

    assert errors == ["More than one category match. Description: 'category1 category2', Matches: ['category1', 'category2']"]  # nopep8
    assert conflicting.category_id is None
    assert single_match.category_id == category1.id


def test_set_categories_by_rules_reports_every_conflict(session: Session):
    __add_categories_with_rules(session)
    session.add_all([make_transaction("1 category1 category2"),
                     make_transaction("2 category1 category2")])
    session.commit()

    errors = categorization.set_categories_by_rules(
        session, session.query(CategoryRule).all())

    assert errors[0] == "More than one category match. Description: '1 category1 category2', Matches: ['category1', 'category2']"  # nopep8
    assert errors[1] == "More than one category match. Description: '2 category1 category2', Matches: ['category1', 'category2']"  # nopep8


def test_distinct_category_names():
    rules = [CategoryRule(category=Category(name="category1"), rule=""),
             CategoryRule(category=Category(name="category2"), rule="")]

    assert categorization.distinct_category_names(rules) == \
        ["category1", "category2"]


def test_distinct_category_names_ignores_repeated_categories():
    category = Category(name="category1")
    rules = [CategoryRule(category=category, rule="a"),
             CategoryRule(category=category, rule="b")]

    assert categorization.distinct_category_names(rules) == ["category1"]


def test_conflict_error_lists_each_conflicting_category_once():
    gas = Category(name="Gas")
    water = Category(name="Water")
    rules = [
        CategoryRule(category=gas, rule="posto"),
        CategoryRule(category=gas, rule="auto posto"),
        CategoryRule(category=water, rule="agua"),
    ]

    error = CategoryRuleConflictError("AUTO POSTO CARAGUATATUBA", rules)

    assert error.message == "More than one category match. Description: 'AUTO POSTO CARAGUATATUBA', Matches: ['Gas', 'Water']"  # nopep8
    assert str(error) == error.message
    assert error.conflicted_category_rules == rules


def test_set_transactions_categories(session: Session):
    transaction = make_transaction("test")
    category = Category(name="TestCategory")
    session.add_all([transaction, category])
    session.flush()
    session.add(TransactionCategory(transaction_id=transaction.id,
                                    category_id=category.id))
    session.commit()

    categorization.set_transactions_categories(session)

    assert session.get(Transaction, transaction.id).category_id == \
        category.id


def test_set_categories_by_user_reports_errors_without_raising(monkeypatch,
                                                               capsys):
    def failing_set(session):
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(categorization, "set_transactions_categories",
                        failing_set)

    categorization.set_categories_by_user(None)  # type: ignore

    assert "Error while setting specific categorization. database unavailable" in capsys.readouterr().out  # nopep8


def __add_categories_with_rules(session: Session) -> list[Category]:
    categories = [Category(name="category1"), Category(name="category2")]
    session.add_all(categories)
    session.flush()
    session.add_all([CategoryRule(category_id=category.id, rule=category.name)
                     for category in categories])
    return categories
