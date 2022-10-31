from sqlalchemy.orm import Session
from sqlite3 import Timestamp
from financial.entities.transaction import Transaction


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


def __get_example_transaction(description: str):
    return Transaction(
        user_id=1,
        user_account="a",
        bank=" ",
        date=Timestamp(year=2022, month=10, day=1),
        description=description,
        value=1,
        balance=1)
