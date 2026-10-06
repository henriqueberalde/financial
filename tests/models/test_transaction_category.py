from factories import make_transaction
from financial.models.transaction import Transaction
from financial.models.category import Category
from financial.models.transaction_category import TransactionCategory


def test_set_transactions_categories(session):
    transaction = make_transaction("test")
    category = Category(name="TestCategory")
    session.add(transaction)
    session.add(category)
    session.flush()

    tc = TransactionCategory(transaction_id=transaction.id,
                             category_id=category.id)

    session.add(tc)
    session.commit()

    TransactionCategory.set_transactions_categories(session)

    t_db = session.get(Transaction, transaction.id)
    print(transaction.id)
    print(t_db.__dict__)

    assert t_db.category_id == category.id


def test_set_categories_by_user_reports_errors_without_raising(monkeypatch,
                                                               capsys):
    def failing_set(session):
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(TransactionCategory,
                        "set_transactions_categories",
                        failing_set)

    TransactionCategory.set_categories_by_user(None)  # type: ignore

    assert "Error while setting specific categorization. database unavailable" in capsys.readouterr().out  # nopep8
