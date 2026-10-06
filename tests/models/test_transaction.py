import hashlib
import pytest

from sqlalchemy.orm import Session
from datetime import datetime
from factories import make_transaction
from financial.models.transaction import Transaction


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


def test_original_value_defaults_to_value():
    transaction = __get_example_transaction("t1")

    assert transaction.original_value == transaction.value


def test_original_value_is_kept_when_given():
    transaction = Transaction(date=datetime(2022, 10, 1), description="t1",
                              value=0, original_value=10, balance=1)

    assert transaction.original_value == 10


def test_original_hash_is_generated_from_date_description_value_and_balance():
    transaction = __get_example_transaction("t1")

    assert transaction.original_hash == hashlib.sha256(
        b"2022-10-01 00:00:00t111").hexdigest()


def test_original_hash_is_kept_when_given():
    transaction = Transaction(date=datetime(2022, 10, 1), description="t1",
                              value=1, balance=1, original_hash="given")

    assert transaction.original_hash == "given"


@pytest.mark.parametrize("value, is_spend, is_gain", [
    (-1, True, False),
    (1, False, True),
    (0, False, False),
])
def test_is_spend_and_is_gain(value, is_spend, is_gain):
    transaction = __get_example_transaction("t1")
    transaction.value = value  # type: ignore

    assert transaction.is_spend() is is_spend
    assert transaction.is_gain() is is_gain


def test_set_context_of_many_rolls_back_on_error(session: Session,
                                                 monkeypatch,
                                                 capsys):
    transaction = __get_example_transaction("t1")
    session.add(transaction)
    session.commit()

    def failing_commit():
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(session, "commit", failing_commit)
    Transaction.set_context_of_many(session, [transaction.id], "context1")

    assert "Error while saving data to db.database unavailable" in capsys.readouterr().out  # nopep8
    assert session.get(Transaction, transaction.id).context is None


def __get_example_transaction(description: str) -> Transaction:
    return make_transaction(description)
