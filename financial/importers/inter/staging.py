from sqlalchemy.orm import Session

from financial.importers.inter.constants import BANK_CODE
from financial.importers.inter.model import InterTransaction
from financial.importers.staging import insert_new_transactions
from financial.models.user import User


def clear(session: Session) -> None:
    """Empty the staging table that receives the imported statement.

    Commits right away: the statement is inserted through another
    connection, which would otherwise wait on this delete's locks.
    """
    session.query(InterTransaction).delete()
    session.commit()


def merge_into_transactions(session: Session, user: User) -> None:
    """Copy staged rows not yet in transactions, matching them by hash."""
    try:
        staged = [row.to_staged() for row in session.query(InterTransaction)]
        insert_new_transactions(session, staged, user, BANK_CODE)
        session.commit()

    except Exception as e:
        print(f"Error while merging transactions from inter.{e}")
        session.rollback()
