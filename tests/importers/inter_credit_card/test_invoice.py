from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest

from financial.importers.inter_credit_card.invoice import (add_months,
                                                           invoice_month,
                                                           parse_value,
                                                           read_invoice)

INVOICE = Path("tests/data/inter_credit_card/2024-06.csv")


def test_invoice_month_comes_from_file_name():
    assert invoice_month(INVOICE) == "2024-06"


def test_invoice_month_rejects_other_file_names():
    with pytest.raises(ValueError, match="must be YYYY-MM.csv"):
        invoice_month(Path("fatura-inter-2024-06.csv"))


@pytest.mark.parametrize("text, value", [
    ("R$\xa015,00", Decimal("-15.00")),
    ("R$\xa01.234,56", Decimal("-1234.56")),
    ("-R$\xa0100,00", Decimal("100.00")),
])
def test_parse_value_turns_purchases_negative(text, value):
    assert parse_value(text) == value


@pytest.mark.parametrize("date, months, expected", [
    (datetime(2023, 7, 6), 10, datetime(2024, 5, 6)),
    (datetime(2024, 1, 31), 1, datetime(2024, 2, 29)),
    (datetime(2024, 11, 15), 2, datetime(2025, 1, 15)),
])
def test_add_months(date, months, expected):
    assert add_months(date, months) == expected


def test_read_invoice_skips_payment_lines():
    descriptions = [line.description for line in read_invoice(INVOICE)]

    assert "PAGTO DEBITO AUTOMATICO" not in descriptions
    assert "PAGAMENTO ON LINE" not in descriptions
    assert "DEVOLUCAO SDO CREDOR" not in descriptions
    assert len(descriptions) == 5


def test_read_invoice_parses_purchases_and_refunds():
    lines = read_invoice(INVOICE)

    purchase, refund = lines[0], lines[3]
    assert purchase.date == datetime(2024, 5, 27)
    assert purchase.description == "MERCADO EXEMPLO SAO PAULO BRA"
    assert purchase.category == "SUPERMERCADO"
    assert purchase.type == "Compra à vista"
    assert purchase.value == Decimal("-1234.56")
    assert refund.value == Decimal("100.00")


def test_read_invoice_moves_installments_to_their_month():
    installment = read_invoice(INVOICE)[-1]

    assert installment.date == datetime(2024, 5, 6)
    assert installment.description == \
        "REVISTA EXEMPLO RIO DE JANEIR BRA - Parcela 11/12"
