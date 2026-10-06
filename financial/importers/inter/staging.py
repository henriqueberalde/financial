from sqlalchemy import text
from sqlalchemy.orm import Session

from financial.importers.inter.constants import BANK_CODE
from financial.importers.inter.model import InterTransaction
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
        session.execute(text("""INSERT INTO transactions (
                                user_id,
                                user_account,
                                bank,
                                date,
                                description,
                                value,
                                original_value,
                                balance,
                                original_hash
                            )
                            SELECT
                                :user_id,
                                :user_account,
                                :bank,
                                it.date,
                                it.description,
                                it.value,
                                it.value,
                                it.balance,
                                it.hash
                            from inter_transactions it
                            left join transactions t on
                                it.hash = t.original_hash
                        where t.id is null;"""), {
                            "user_id": user.id,
                            "user_account": user.account,
                            "bank": BANK_CODE,
                        })
        session.commit()

    except Exception as e:
        print(f"Error while merging transactions from inter.{e}")
        session.rollback()
