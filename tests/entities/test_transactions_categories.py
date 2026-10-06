from factories import make_transaction
from financial.entities.transaction import Transaction
from financial.entities.category import Category
from financial.entities.transactions_categories import TransactionsCategories


def test_set_transactions_categories(session):
    transaction = make_transaction("test")
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


def test_set_categories_by_user_reports_errors_without_raising(monkeypatch,
                                                               capsys):
    def failing_set(session):
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(TransactionsCategories,
                        "set_transactions_categories",
                        failing_set)

    TransactionsCategories.set_categories_by_user(None)  # type: ignore

    assert "Error while setting specific categorization. database unavailable" in capsys.readouterr().out  # nopep8
