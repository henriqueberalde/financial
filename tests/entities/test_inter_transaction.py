from sqlalchemy.orm import Session
from sqlite3 import Timestamp
from financial.entities.transaction import Transaction
from financial.entities.inter_transaction import InterTransaction
from financial.entities.user import User


def test_merge_to_transactions_add_columns(session: Session):
    bank = "077"
    user = User(99, "test_user_account")

    it1 = InterTransaction(
        date=Timestamp(2022, 1, 1),
        description="Test1",
        value=1.1,
        balance=111.1)

    session.add(it1)
    session.commit()

    InterTransaction.merge_to_transactions(session, user)

    transactions = session.query(Transaction).all()

    assert len(transactions) == 1
    assert transactions[0].bank == bank
    assert transactions[0].user_id == user.id
    assert transactions[0].user_account == user.account


def test_merge_to_transactions(session: Session):
    bank = "077"
    user = User(1, "123")

    it1 = InterTransaction(
        date=Timestamp(2022, 1, 1),
        description="Test1",
        value=1.1,
        balance=111.1)

    it2 = InterTransaction(
        date=Timestamp(2022, 1, 1),
        description="Test2",
        value=2.2,
        balance=222.2)

    session.add(it1)
    session.add(it2)
    session.commit()

    InterTransaction.merge_to_transactions(session, user)

    transactions = session.query(Transaction).all()

    assert len(transactions) == 2

    assert transactions[0].date == it1.date
    assert transactions[0].description == it1.description
    assert transactions[0].value == it1.value
    assert transactions[0].balance == it1.balance
    assert transactions[0].bank == bank
    assert transactions[0].user_id == user.id
    assert transactions[0].user_account == user.account

    assert transactions[1].date == it2.date
    assert transactions[1].description == it2.description
    assert transactions[1].value == it2.value
    assert transactions[1].balance == it2.balance
    assert transactions[1].bank == bank
    assert transactions[1].user_id == user.id
    assert transactions[1].user_account == user.account


def test_merge_to_transactions_existing_transactions(session: Session):
    bank = "077"
    user = User(1, "123")

    it1 = InterTransaction(
        date=Timestamp(2022, 1, 1),
        description="Test1",
        value=1.1,
        balance=111.1)

    it2 = InterTransaction(
        date=Timestamp(2022, 1, 1),
        description="Test2",
        value=2.2,
        balance=222.2)

    it3 = InterTransaction(
        date=Timestamp(2022, 1, 1),
        description="Test3",
        value=3.3,
        balance=333.3)

    t1 = Transaction(
        date=Timestamp(2022, 1, 1),
        description="Test1",
        value=1.1,
        balance=111.1,
        bank="077",
        user_id=1,
        user_account="123")

    t3 = Transaction(
        date=Timestamp(2022, 1, 1),
        description="Test3",
        value=3.3,
        balance=333.3,
        bank="077",
        user_id=1,
        user_account="123")

    session.add(it1)
    session.add(it2)
    session.add(it3)
    session.add(t1)
    session.add(t3)
    session.commit()

    InterTransaction.merge_to_transactions(session, user)

    transactions = session.query(Transaction).all()

    assert len(transactions) == 3

    assert transactions[2].date == it2.date
    assert transactions[2].description == it2.description
    assert transactions[2].value == it2.value
    assert transactions[2].balance == it2.balance
    assert transactions[2].bank == bank
    assert transactions[2].user_id == user.id
    assert transactions[2].user_account == user.account


def test_merge_to_transactions_set_original_value(session):
    user = User(99, "test_user_account")

    it1 = InterTransaction(
        date=Timestamp(2022, 1, 1),
        description="Test1",
        value=34,
        balance=111.1)

    session.add(it1)
    session.commit()

    InterTransaction.merge_to_transactions(session, user)

    transactions = session.query(Transaction).all()

    assert len(transactions) == 1
    assert transactions[0].original_value == transactions[0].value
