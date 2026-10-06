"""Logic shared by the importers to move staged rows into transactions."""
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from financial.models.transaction import Transaction
from financial.models.user import User


@dataclass(frozen=True)
class StagedTransaction:
    date: datetime
    description: str
    value: Decimal
    balance: Decimal | None
    hash: str


def insert_new_transactions(session: Session,
                            staged: Iterable[StagedTransaction],
                            user: User,
                            bank: str) -> list[Transaction]:
    """Add the staged rows whose hash is not in transactions yet.

    Flushes without committing, so callers decide the transaction scope.
    Returns the transactions that were added.
    """
    existing = {h for (h,) in session.query(Transaction.original_hash)}
    added = [
        Transaction(user_id=user.id,
                    user_account=user.account,
                    bank=bank,
                    date=row.date,
                    description=row.description,
                    value=row.value,
                    original_value=row.value,
                    balance=row.balance,
                    original_hash=row.hash)
        for row in staged if row.hash not in existing
    ]
    session.add_all(added)
    session.flush()

    return added
