import pytest
from sqlalchemy.orm import Session
from sqlite3 import Timestamp
from financial.entities.transaction import Transaction
from financial.entities.category import Category
from financial.entities.category_rule import CategoryRule
from financial.entities.normalization_error import NormalizationError


def test_transaction_set_context_of_many(session: Session):
    context = "context1"

    t1 = __get_example_transaction("t1")
    t2 = __get_example_transaction("t2")
    t3 = __get_example_transaction("t3")

    session.add(t1)
    session.add(t2)
    session.add(t3)

    session.commit()
    Transaction.set_context_of_many(session, [t1.id, t3.id], context)

    assert session.get(Transaction, t1.id).context == context
    assert session.get(Transaction, t2.id).context is None
    assert session.get(Transaction, t3.id).context == context


def test_transaction_set_context_of_many_str_parameter(session: Session):
    context = "context1"

    t1 = __get_example_transaction("t1")
    t2 = __get_example_transaction("t2")
    t3 = __get_example_transaction("t3")

    session.add(t1)
    session.add(t2)
    session.add(t3)

    session.commit()
    Transaction.set_context_of_many(session, f"{t2.id} {t3.id}", context)

    assert session.get(Transaction, t1.id).context is None
    assert session.get(Transaction, t2.id).context == context
    assert session.get(Transaction, t3.id).context == context


def test_set_categories_by_rules(session: Session):
    c1 = __get_example_category("category1")
    c2 = __get_example_category("category2")

    session.add(c1)
    session.add(c2)
    session.flush()

    r1 = __get_example_category_rule(int(str(c1.id)), "category1")
    r2 = __get_example_category_rule(int(str(c2.id)), "category2")

    session.add(r1)
    session.add(r2)

    t1 = __get_example_transaction("PAGAMENTO DE CONVENIO - category1")
    t2 = __get_example_transaction("PAGAMENTO DE CONVENIO - category2")
    t3 = __get_example_transaction("PAGAMENTO DE CONVENIO - Nao categorizado")

    session.add(t1)
    session.add(t2)
    session.add(t3)

    session.commit()

    Transaction.set_categories_by_rules(session,
                                        session.query(CategoryRule).all())

    assert t1.category_id == c1.id
    assert t2.category_id == c2.id
    assert t3.category_id is None


def test_set_categories_by_rules_many_matched_categories(session: Session):
    c1 = __get_example_category("category1")
    c2 = __get_example_category("category2")

    session.add(c1)
    session.add(c2)
    session.flush()

    r1 = __get_example_category_rule(int(str(c1.id)), "category1")
    r2 = __get_example_category_rule(int(str(c2.id)), "category2")

    session.add(r1)
    session.add(r2)

    t1 = __get_example_transaction("category1 category2")

    session.add(t1)

    session.commit()

    with pytest.raises(
            NormalizationError,
            match="More than one category match\\. " +
                  "Description: 'category1 category2', " +
                  "Matches: \\['category1', 'category2'\\]"
            ):
        Transaction.set_categories_by_rules(session,
                                            session.query(CategoryRule).all())


def test_set_categories_by_rules_many_conflict_erros(session: Session):
    c1 = __get_example_category("category1")
    c2 = __get_example_category("category2")

    session.add(c1)
    session.add(c2)
    session.flush()

    r1 = __get_example_category_rule(int(str(c1.id)), "category1")
    r2 = __get_example_category_rule(int(str(c2.id)), "category2")

    session.add(r1)
    session.add(r2)

    t1 = __get_example_transaction("1 category1 category2")
    t2 = __get_example_transaction("2 category1 category2")

    session.add(t1)
    session.add(t2)

    session.commit()

    with pytest.raises(NormalizationError) as e_info:
        Transaction.set_categories_by_rules(session,
                                            session.query(CategoryRule).all())

    assert e_info.value.messages[0] == "More than one category match. Description: '1 category1 category2', Matches: ['category1', 'category2']"  # nopep8
    assert e_info.value.messages[1] == "More than one category match. Description: '2 category1 category2', Matches: ['category1', 'category2']"  # nopep8


def __get_example_transaction(description: str) -> Transaction:
    return Transaction(
        user_id=1,
        user_account="a",
        bank=" ",
        date=Timestamp(year=2022, month=10, day=1),
        description=description,
        value=1,
        balance=1)


def __get_example_category(name: str) -> Category:
    return Category(name=name)


def __get_example_category_rule(category_id: int, rule: str) -> CategoryRule:
    return CategoryRule(
        category_id=category_id,
        rule=rule)
