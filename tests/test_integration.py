from sqlalchemy.orm import Session
from financial.inter.transactions_importer import TransactionsImporter
from financial.entities.inter_transaction import InterTransaction
from financial.entities.user import User
from financial.entities.adjustement import Adjustment
from financial.entities.transaction import Transaction
from sqlalchemy.engine.row import Row


def test_keep_original_transaction_after_merge(session: Session):
    # Import Transactions
    importer = TransactionsImporter(session)
    importer.import_from_csv("tests/test_import_adjustment.csv")

    # Merge them
    InterTransaction.merge_to_transactions(session, User(1, "234543"))

    # Change them (setting adjustment)
    transactions = session.query(Transaction).all()

    Adjustment.add(session, "Test", [transactions[0].id, transactions[1].id])

    # Merge the same Transactions again
    InterTransaction.merge_to_transactions(session, User(1, "234543"))

    # Nothing should be changed in transactions
    #   because theese transactions have being already merged
    #   dispite it is diferent
    assert session.query(Transaction).count() == 2
