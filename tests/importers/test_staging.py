from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from factories import make_transaction
from financial.importers.staging import StagedTransaction
from financial.importers.staging import insert_new_transactions
from financial.models.transaction import Transaction
from financial.models.user import User

USER = User(7, "account")


def test_insert_new_transactions_copies_staged_fields(session: Session):
    staged = __staged("new", Decimal("-10.50"), balance=Decimal("90.00"))

    added = insert_new_transactions(session, [staged], USER, "077")

    transaction = session.query(Transaction).one()
    assert added == [transaction]
    assert transaction.user_id == 7
    assert transaction.user_account == "account"
    assert transaction.bank == "077"
    assert transaction.date == staged.date
    assert transaction.description == "new"
    assert transaction.value == transaction.original_value == Decimal("-10.50")
    assert transaction.balance == Decimal("90.00")
    assert transaction.original_hash == "hash-new"


def test_insert_new_transactions_skips_hashes_already_in_transactions(
        session: Session):
    session.add(make_transaction("existing", original_hash="hash-existing"))
    session.commit()

    added = insert_new_transactions(
        session,
        [__staged("existing", Decimal("-1")), __staged("new", Decimal("-2"))],
        USER,
        "077")

    assert [t.description for t in added] == ["new"]
    assert session.query(Transaction).count() == 2


def test_insert_new_transactions_accepts_rows_without_balance(
        session: Session):
    insert_new_transactions(session, [__staged("card", Decimal("-5"))],
                            USER, "077")

    assert session.query(Transaction).one().balance is None


def test_insert_new_transactions_does_not_commit(session: Session):
    insert_new_transactions(session, [__staged("new", Decimal("-1"))],
                            USER, "077")
    session.rollback()

    assert session.query(Transaction).count() == 0


def __staged(description: str,
             value: Decimal,
             balance: Decimal | None = None) -> StagedTransaction:
    return StagedTransaction(date=datetime(2024, 5, 1),
                             description=description,
                             value=value,
                             balance=balance,
                             hash=f"hash-{description}")
