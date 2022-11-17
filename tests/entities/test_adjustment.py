import pytest

from datetime import datetime
from financial.entities.transaction import Transaction
from financial.entities.adjustement import Adjustment
from sqlalchemy.orm import Session


def test_gains_gratter_them_spends(session: Session):
    spend1 = __transaction(session, "spend")
    spend2 = __transaction(session, "spend")
    gain1 = __transaction(session, "gain")
    gain2 = __transaction(session, "gain")
    gain3 = __transaction(session, "gain")

    spend1.value = -10  # type: ignore
    spend2.value = -1  # type: ignore
    gain1.value = 76  # type: ignore
    gain2.value = 45  # type: ignore
    gain3.value = 1  # type: ignore

    session.flush()

    Adjustment.add(
        session,
        "Test Reason",
        [spend1, spend2, gain1, gain2, gain3]
    )

    session.refresh(spend1)
    session.refresh(spend2)
    session.refresh(gain1)
    session.refresh(gain2)
    session.refresh(gain3)

    assert spend1.value == 0
    assert spend2.value == 0

    assert gain1.value == 76
    assert gain2.value == 35
    assert gain3.value == 0


def test_spends_gratter_them_gains(session: Session):
    spend1 = __transaction(session, "spend")
    spend2 = __transaction(session, "spend")
    gain1 = __transaction(session, "gain")
    gain2 = __transaction(session, "gain")
    gain3 = __transaction(session, "gain")

    spend1.value = -1000  # type: ignore
    spend2.value = -1  # type: ignore
    gain1.value = 250  # type: ignore
    gain2.value = 250  # type: ignore
    gain3.value = 1  # type: ignore

    Adjustment.add(
        session,
        "Test Reason",
        [spend1, spend2, gain1, gain2, gain3]
    )

    session.refresh(spend1)
    session.refresh(spend2)
    session.refresh(gain1)
    session.refresh(gain2)
    session.refresh(gain3)

    assert spend1.value == -500
    assert spend2.value == 0

    assert gain1.value == 0
    assert gain2.value == 0
    assert gain3.value == 0


def test_when_transaction_is_passed_success(session: Session):
    spend = __transaction(session, "spend")
    gain = __transaction(session, "gain")

    Adjustment.add(
        session,
        "Test Reason",
        [spend, gain]
    )

    a = session.query(Adjustment).all()

    assert len(a) == 1
    assert len(a[0].transactions) == 2
    assert a[0].transactions[0].original_value == -30
    assert a[0].transactions[1].original_value == 30
    assert a[0].transactions[0].value == 0
    assert a[0].transactions[1].value == 0


def test_when_int_is_passed_success(session: Session):
    __transaction(session, "spend")
    __transaction(session, "gain")

    Adjustment.add(
        session,
        "Test Reason",
        [1, 2]
    )

    a = session.query(Adjustment).all()

    assert len(a) == 1
    assert len(a[0].transactions) == 2
    assert a[0].transactions[0].original_value == -30
    assert a[0].transactions[1].original_value == 30
    assert a[0].transactions[0].value == 0
    assert a[0].transactions[1].value == 0


def test_when_many_transactions_success(session: Session):
    spend1 = __transaction(session, "spend")
    spend2 = __transaction(session, "spend")
    spend3 = __transaction(session, "spend")
    gain1 = __transaction(session, "gain")
    gain2 = __transaction(session, "gain")
    gain3 = __transaction(session, "gain")

    Adjustment.add(
        session,
        "Test Reason",
        [spend1, spend2, spend3, gain1, gain2, gain3],
    )

    a = session.query(Adjustment).all()

    assert len(a) == 1
    assert len(a[0].transactions) == 6


def test_when_only_spend_error(session: Session):
    spend1 = __transaction(session, "spend")
    spend2 = __transaction(session, "spend")

    with pytest.raises(
            Exception,
            match="Transactions must have at least one spend and one gain"):
        Adjustment.add(
            session,
            "Test Reason",
            [spend1, spend2],
        )


def test_when_only_gain_error(session: Session):
    gain1 = __transaction(session, "gain")
    gain2 = __transaction(session, "gain")

    with pytest.raises(
            Exception,
            match="Transactions must have at least one spend and one gain"):
        Adjustment.add(
            session,
            "Test Reason",
            [gain1, gain2],
        )


def test_when_empty_transactions_error(session: Session):
    with pytest.raises(
            Exception,
            match="Transactions must have at least one spend and one gain"):
        Adjustment.add(
            session,
            "Test Reason",
            [],
        )


def __transaction(session: Session, type: str):
    value = 0

    if type == 'spend':
        value = -30
    else:
        value = 30

    t = Transaction(
        user_id=1,
        user_account="a",
        bank=" ",
        date=datetime(year=2022, month=10, day=1),
        description=f"{type} 1",
        value=value,
        balance=1
    )

    session.add(t)
    session.commit()

    return t
