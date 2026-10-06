from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from factories import make_transaction
from financial.importers.inter_credit_card import staging
from financial.importers.inter_credit_card.importer import CreditCardImporter
from financial.importers.inter_credit_card.model import \
    InterCreditCardTransaction
from financial.models.transaction import Transaction
from financial.models.user import User

INVOICES = Path("tests/data/inter_credit_card")
JUNE_TOTAL = Decimal("1186.96")  # purchases minus refund of 2024-06.csv
JULY_TOTAL = Decimal("25.00")
USER = User(1, "123")
PAYMENT = 'Pagamento efetuado: "Debito Automatico Fatura Cartao Inter"'


def test_merge_adds_lines_and_deducts_them_from_the_payment(session: Session):
    payment = __payment(session, datetime(2024, 6, 12), "-1186.96")
    __stage(session, "2024-06.csv")

    results = staging.merge_into_transactions(session, USER)

    assert results == [staging.MonthMerge("2024-06", 5, JUNE_TOTAL)]
    assert payment.value == 0
    assert payment.original_value == Decimal("-1186.96")
    card = session.query(Transaction).filter(Transaction.balance.is_(None))
    assert card.count() == 5
    assert {t.bank for t in card} == {"077"}
    assert session.query(InterCreditCardTransaction).count() == 0


def test_merge_keeps_what_the_invoice_lines_do_not_explain(session: Session):
    payment = __payment(session, datetime(2024, 6, 12), "-1200.00")
    __stage(session, "2024-06.csv")

    staging.merge_into_transactions(session, USER)

    assert payment.value == Decimal("-13.04")


def test_merge_uses_payments_of_the_month_in_date_order(session: Session):
    first = __payment(session, datetime(2024, 6, 1), "-1000.00")
    second = __payment(session, datetime(2024, 6, 12), "-186.96")
    __stage(session, "2024-06.csv")

    staging.merge_into_transactions(session, USER)

    assert (first.value, second.value) == (0, 0)


def test_merge_uses_previous_month_leftover_after_the_months_payments(
        session: Session):
    advance = __payment(session, datetime(2024, 5, 26), "-1000.00")
    june = __payment(session, datetime(2024, 6, 12), "-186.96")
    __stage(session, "2024-06.csv")

    staging.merge_into_transactions(session, USER)

    assert (june.value, advance.value) == (0, 0)


def test_merge_prefers_the_months_payment_over_previous_ones(
        session: Session):
    duplicated = __payment(session, datetime(2024, 5, 13), "-5907.96")
    june = __payment(session, datetime(2024, 6, 12), "-1186.96")
    __stage(session, "2024-06.csv")

    staging.merge_into_transactions(session, USER)

    assert june.value == 0
    assert duplicated.value == Decimal("-5907.96")


def test_merge_ignores_card_purchases_and_other_transactions(
        session: Session):
    session.add_all([
        make_transaction("Fatura Cartao Inter compra", -5000, balance=None,
                         date=datetime(2024, 6, 1)),
        make_transaction("Pix enviado", -5000, date=datetime(2024, 6, 1)),
        make_transaction(PAYMENT, -5000, bank="001",
                         date=datetime(2024, 6, 1)),
    ])
    session.commit()
    __stage(session, "2024-06.csv")

    results = staging.merge_into_transactions(session, USER)

    assert "No credit card payment found for invoice 2024-06" in \
        str(results[0].error)


def test_merge_keeps_a_month_without_payment_staged(session: Session):
    july = __payment(session, datetime(2024, 7, 12), "-25.00")
    __stage(session, "2024-06.csv")
    __stage(session, "2024-07.csv")

    results = staging.merge_into_transactions(session, USER)

    assert results[0].invoice_month == "2024-06"
    assert results[0].merged == 0
    assert results[0].error == (
        "No credit card payment found for invoice 2024-06: "
        "R$ 1186.96 of R$ 1186.96 not covered")
    assert results[1] == staging.MonthMerge("2024-07", 1, JULY_TOTAL)
    assert july.value == 0
    assert staging.staged_months(session) == ["2024-06"]
    assert session.query(Transaction).filter(
        Transaction.balance.is_(None)).count() == 1


def test_merge_rolls_back_a_month_whose_payment_is_too_small(
        session: Session):
    payment = __payment(session, datetime(2024, 6, 12), "-100.00")
    __stage(session, "2024-06.csv")

    results = staging.merge_into_transactions(session, USER)

    assert "R$ 1086.96 of R$ 1186.96 not covered" in str(results[0].error)
    session.refresh(payment)
    assert payment.value == Decimal("-100.00")
    assert staging.staged_months(session) == ["2024-06"]


def test_merge_does_not_deduct_lines_merged_before(session: Session):
    payment = __payment(session, datetime(2024, 6, 12), "-1186.96")
    __stage(session, "2024-06.csv")
    staging.merge_into_transactions(session, USER)
    __stage(session, "2024-06.csv")

    results = staging.merge_into_transactions(session, USER)

    assert results == [staging.MonthMerge("2024-06", 0, Decimal(0))]
    assert payment.value == 0
    assert staging.staged_months(session) == []


def test_merge_rejects_an_invoice_that_is_a_credit(session: Session):
    session.add(InterCreditCardTransaction(
        invoice_month="2024-06", date=datetime(2024, 6, 1),
        description="ESTORNO", value=Decimal("50.00"), hash="refund"))
    session.commit()

    results = staging.merge_into_transactions(session, USER)

    assert results[0].error == \
        "Invoice 2024-06 is a credit of R$ 50.00; nothing to deduct"


def test_merge_rolls_back_and_raises_unexpected_errors(session: Session):
    __stage(session, "2024-06.csv")

    with pytest.raises(AttributeError):
        staging.merge_into_transactions(session, None)  # type: ignore

    assert staging.staged_months(session) == ["2024-06"]


def __payment(session: Session, date: datetime, value: str) -> Transaction:
    payment = make_transaction(PAYMENT, Decimal(value), date=date)
    session.add(payment)
    session.commit()
    return payment


def __stage(session: Session, name: str) -> None:
    CreditCardImporter(session).import_file(INVOICES / name)
