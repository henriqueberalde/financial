import hashlib

from datetime import datetime
from financial.importers.inter.model import InterTransaction


def test_hash_is_generated_from_date_description_value_and_balance():
    inter_transaction = InterTransaction(date=datetime(2022, 1, 1),
                                         description="Test1",
                                         value=1.1,
                                         balance=111.1)

    assert inter_transaction.hash == hashlib.sha256(
        b"2022-01-01 00:00:00Test11.1111.1").hexdigest()


def test_hash_is_kept_when_given():
    inter_transaction = InterTransaction(date=datetime(2022, 1, 1),
                                         description="Test1",
                                         value=1.1,
                                         balance=111.1,
                                         hash="given")

    assert inter_transaction.hash == "given"
