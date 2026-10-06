from sqlalchemy.orm import Session

from factories import make_transaction
from financial.models.adjustment import Adjustment


def test_gains_and_spends_split_transactions_by_sign(session: Session):
    spend = make_transaction("spend", -30)
    gain = make_transaction("gain", 30)

    adjustment = Adjustment(reason="Test Reason", transactions=[spend, gain])
    session.add(adjustment)

    assert adjustment.spends() == [spend]
    assert adjustment.gains() == [gain]
