import hashlib
import pytest

from datetime import datetime
from factories import make_transaction
from financial.models.transaction import Transaction


def test_original_value_defaults_to_value():
    transaction = make_transaction("t1")

    assert transaction.original_value == transaction.value


def test_original_value_is_kept_when_given():
    transaction = Transaction(date=datetime(2022, 10, 1), description="t1",
                              value=0, original_value=10, balance=1)

    assert transaction.original_value == 10


def test_original_hash_is_generated_from_date_description_value_and_balance():
    transaction = make_transaction("t1")

    assert transaction.original_hash == hashlib.sha256(
        b"2022-10-01 00:00:00t111").hexdigest()


def test_original_hash_is_kept_when_given():
    transaction = Transaction(date=datetime(2022, 10, 1), description="t1",
                              value=1, balance=1, original_hash="given")

    assert transaction.original_hash == "given"


@pytest.mark.parametrize("value, is_spend, is_gain", [
    (-1, True, False),
    (1, False, True),
    (0, False, False),
])
def test_is_spend_and_is_gain(value, is_spend, is_gain):
    transaction = make_transaction("t1")
    transaction.value = value  # type: ignore

    assert transaction.is_spend() is is_spend
    assert transaction.is_gain() is is_gain
