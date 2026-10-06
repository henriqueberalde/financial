from collections import Counter
from pathlib import Path

from sqlalchemy.orm import Session

from financial.hashing import sha256
from financial.importers.base import BaseTransactionsImporter
from financial.importers.inter.constants import BANK_CODE
from financial.importers.inter_credit_card.constants import DATA_DIR
from financial.importers.inter_credit_card.invoice import (InvoiceLine,
                                                           invoice_month,
                                                           read_invoice)
from financial.importers.inter_credit_card.model import \
    InterCreditCardTransaction


class CreditCardImporter(BaseTransactionsImporter):
    """Stages Inter credit card invoices, without merging them."""

    def __init__(self, session: Session) -> None:
        super().__init__(BANK_CODE)
        self.session = session

    @staticmethod
    def invoice_files(directory: Path = DATA_DIR) -> list[Path]:
        return sorted(directory.glob("*.csv"))

    def import_file(self, path: Path) -> int:
        """Stage the lines of an invoice file, replacing the ones of the
        same invoice month staged before. Returns how many were staged."""
        month = invoice_month(path)
        lines = read_invoice(path)

        self.session.query(InterCreditCardTransaction) \
            .filter_by(invoice_month=month).delete()
        self.session.add_all(_staging_rows(month, lines))
        self.session.commit()

        return len(lines)


def _staging_rows(month: str, lines: list[InvoiceLine]) \
        -> list[InterCreditCardTransaction]:
    # Identical lines are legit (e.g. two equal IOF charges on the same day),
    # so the hash includes how many times the line appeared before
    seen: Counter[tuple] = Counter()
    rows = []

    for line in lines:
        key = (line.date, line.description, line.value)
        rows.append(InterCreditCardTransaction(
            invoice_month=month,
            date=line.date,
            description=line.description,
            category=line.category,
            type=line.type,
            value=line.value,
            hash=sha256(f"{month}{line.date:%Y-%m-%d}{line.description}"
                        f"{line.value}{seen[key]}")))
        seen[key] += 1

    return rows
