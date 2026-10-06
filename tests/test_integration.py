from sqlalchemy.orm import Session
from financial.importers.inter.importer import TransactionsImporter
from financial.importers.inter.model import InterTransaction
from financial.models.user import User
from financial.services import adjustments
from financial.models.transaction import Transaction


def test_keep_original_transaction_after_merge(session: Session):
    # Import Transactions
    importer = TransactionsImporter(session)
    importer.import_from_csv("tests/data/inter_statement_adjustment.csv")

    # Merge them
    InterTransaction.merge_to_transactions(session, User(1, "234543"))

    # Change them (setting adjustment)
    transactions = session.query(Transaction).all()

    adjustments.add_adjustment(session, "Test",
                               [transactions[0].id, transactions[1].id])

    # Merge the same Transactions again
    InterTransaction.merge_to_transactions(session, User(1, "234543"))

    # Nothing should be changed in transactions
    #   because theese transactions have being already merged
    #   dispite it is diferent
    assert session.query(Transaction).count() == 2
