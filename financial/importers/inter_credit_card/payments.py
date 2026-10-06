import re

from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from financial.importers.inter.constants import BANK_CODE
from financial.importers.inter_credit_card.constants import \
    PAYMENT_DESCRIPTION_PATTERN
from financial.importers.inter_credit_card.invoice import add_months
from financial.models.transaction import Transaction


class CreditCardMergeError(Exception):
    pass


def deduct_invoice(session: Session,
                   invoice_month: str,
                   amount: Decimal) -> list[Transaction]:
    """Deduct the invoice amount from the value of the checking account
    transactions that paid it, keeping their original_value.

    Payments of the invoice month are used first, in date order, then what
    is left of the previous month's ones (invoices paid in advance).
    Raises CreditCardMergeError when they do not cover the amount.
    """
    remaining = amount
    used: list[Transaction] = []

    for payment in _payments(session, invoice_month):
        deducted = min(remaining, -payment.value)  # type: ignore
        payment.value += deducted  # type: ignore
        remaining -= deducted
        used.append(payment)

        if remaining == 0:
            return used

    raise CreditCardMergeError(
        f"No credit card payment found for invoice {invoice_month}: "
        f"R$ {remaining:.2f} of R$ {amount:.2f} not covered")


def _payments(session: Session, invoice_month: str) -> list[Transaction]:
    month_start = datetime.strptime(invoice_month, "%Y-%m")
    candidates = session.query(Transaction).filter(
        Transaction.bank == BANK_CODE,
        Transaction.balance.isnot(None),  # card purchases have no balance
        Transaction.value < 0,
        Transaction.date >= add_months(month_start, -1),
        Transaction.date < add_months(month_start, 1),
    ).order_by(Transaction.date, Transaction.id)

    payments = [t for t in candidates
                if re.search(PAYMENT_DESCRIPTION_PATTERN,
                             str(t.description), re.IGNORECASE)]
    current = [p for p in payments if p.date >= month_start]
    previous = [p for p in payments if p.date < month_start]

    return current + previous
