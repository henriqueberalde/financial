from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.orm import Session

from financial.importers.inter.constants import BANK_CODE
from financial.importers.inter_credit_card.model import \
    InterCreditCardTransaction
from financial.importers.inter_credit_card.payments import (
    CreditCardMergeError, deduct_invoice)
from financial.importers.staging import insert_new_transactions
from financial.models.user import User


@dataclass(frozen=True)
class MonthMerge:
    invoice_month: str
    merged: int
    deducted: Decimal
    error: str | None = None


def staged_months(session: Session) -> list[str]:
    rows = session.query(InterCreditCardTransaction.invoice_month).distinct()
    return sorted(month for (month,) in rows)


def merge_into_transactions(session: Session, user: User) -> list[MonthMerge]:
    """Merge the staged invoices one month at a time, oldest first.

    A month whose payment is not found is rolled back and stays staged to
    be merged again; the other months are still merged.
    """
    results = []

    for month in staged_months(session):
        try:
            results.append(merge_month(session, month, user))
            session.commit()
        except CreditCardMergeError as e:
            session.rollback()
            results.append(MonthMerge(month, 0, Decimal(0), str(e)))
        except Exception:
            session.rollback()
            raise

    return results


def merge_month(session: Session, month: str, user: User) -> MonthMerge:
    """Add the month's invoice lines to transactions and deduct their total
    from the card payment. Lines merged before are neither added nor
    deducted again. Does not commit."""
    staged = session.query(InterCreditCardTransaction) \
        .filter_by(invoice_month=month) \
        .order_by(InterCreditCardTransaction.id)
    added = insert_new_transactions(session,
                                    [row.to_staged() for row in staged],
                                    user,
                                    BANK_CODE)
    amount = -sum((t.value for t in added), Decimal(0))  # type: ignore

    if amount < 0:
        raise CreditCardMergeError(
            f"Invoice {month} is a credit of R$ {-amount:.2f}; "
            "nothing to deduct")

    if amount > 0:
        deduct_invoice(session, month, amount)

    session.query(InterCreditCardTransaction) \
        .filter_by(invoice_month=month).delete()

    return MonthMerge(month, len(added), amount)
