from datetime import datetime
from decimal import Decimal

from financial.importers.inter_credit_card.model import \
    InterCreditCardTransaction


def test_to_staged_has_no_balance():
    row = InterCreditCardTransaction(invoice_month="2024-06",
                                     date=datetime(2024, 5, 27),
                                     description="MERCADO",
                                     value=Decimal("-10.00"),
                                     hash="hash")

    staged = row.to_staged()

    assert (staged.date, staged.description, staged.value, staged.hash) == \
        (datetime(2024, 5, 27), "MERCADO", Decimal("-10.00"), "hash")
    assert staged.balance is None
