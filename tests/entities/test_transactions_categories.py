from sqlalchemy.inspection import inspect
from sqlite3 import Timestamp
from financial.entities.transaction import Transaction
from financial.entities.category import Category
from financial.entities.transactions_categories import TransactionsCategories


def test_set_transactions_categories(session):
    transaction = Transaction(
        user_id=1,
        user_account="a",
        bank=" ",
        date=Timestamp(year=2022, month=10, day=1),
        description="test",
        value=1,
        balance=1)
    category = Category(name="TestCategory")
    session.add(transaction)
    session.add(category)
    session.flush()

    tc = TransactionsCategories(transaction_id=transaction.id,
                                category_id=category.id)

    session.add(tc)
    session.commit()

    TransactionsCategories.set_transactions_categories(session)

    t_db = session.get(Transaction, transaction.id)
    print(transaction.id)
    print(t_db.__dict__)

    assert t_db.category_id == category.id
