from sqlalchemy.orm import Session

from factories import make_transaction
from financial.models.transaction import Transaction
from financial.services import transactions


def test_set_context(session: Session):
    context = "context1"

    t1 = make_transaction("t1")
    t2 = make_transaction("t2")
    t3 = make_transaction("t3")

    session.add(t1)
    session.add(t2)
    session.add(t3)

    session.commit()
    transactions.set_context(session, [t1.id, t3.id], context)

    assert session.get(Transaction, t1.id).context == context
    assert session.get(Transaction, t2.id).context is None
    assert session.get(Transaction, t3.id).context == context


def test_set_context_with_space_separated_ids(session: Session):
    context = "context1"

    t1 = make_transaction("t1")
    t2 = make_transaction("t2")
    t3 = make_transaction("t3")

    session.add(t1)
    session.add(t2)
    session.add(t3)

    session.commit()
    transactions.set_context(session, f"{t2.id} {t3.id}", context)

    assert session.get(Transaction, t1.id).context is None
    assert session.get(Transaction, t2.id).context == context
    assert session.get(Transaction, t3.id).context == context


def test_set_context_rolls_back_on_error(session: Session,
                                         monkeypatch,
                                         capsys):
    transaction = make_transaction("t1")
    session.add(transaction)
    session.commit()

    def failing_commit():
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(session, "commit", failing_commit)
    transactions.set_context(session, [transaction.id], "context1")

    assert "Error while saving data to db.database unavailable" in capsys.readouterr().out  # nopep8
    assert session.get(Transaction, transaction.id).context is None
