from datetime import datetime

import pandas as pd
import pytest

from sqlalchemy.orm import Session

from factories import make_transaction
from financial.models.category import Category
from financial.services.analytics import ledger


def test_load_classifies_every_transaction(session: Session):
    market = Category(name="Market", sector="Essential")
    session.add_all([
        make_transaction("COMPRA CARTAO - NO ESTABELECIMENTO PADARIA",
                         -10, category=market),
        make_transaction("PIX RECEBIDO - JOHN", 50),
        make_transaction("APLICACAO CDB", -100),
        make_transaction("CARD PURCHASE", -5, balance=None),
    ])
    session.commit()

    frame = ledger.load(session)

    assert frame["kind"].tolist() == [ledger.EXPENSE, ledger.INCOME,
                                      ledger.INVESTMENT, ledger.EXPENSE]
    assert frame["category"].tolist() == ["Market", "Sem categoria",
                                          "Sem categoria", "Sem categoria"]
    assert frame["sector"].tolist()[:2] == ["Essential", "Sem categoria"]
    assert frame["merchant"].tolist()[:2] == ["PADARIA", "JOHN"]
    assert frame["source"].tolist() == [ledger.ACCOUNT, ledger.ACCOUNT,
                                        ledger.ACCOUNT, ledger.CARD]
    assert frame["month"].iloc[0] == pd.Period("2022-10", freq="M")


def test_load_without_transactions(session: Session):
    frame = ledger.load(session)

    assert frame.empty
    assert ledger.last_complete_month(frame) is None


@pytest.mark.parametrize("days, expected", [
    (["2026-01-31", "2026-02-10"], "2026-01"),
    (["2026-01-10", "2026-02-28"], "2026-02"),
    (["2026-02-10"], "2026-02"),
])
def test_last_complete_month(session: Session, days: list[str],
                             expected: str):
    session.add_all([make_transaction(date=datetime.fromisoformat(day))
                     for day in days])
    session.commit()

    assert str(ledger.last_complete_month(ledger.load(session))) == expected


@pytest.mark.parametrize("description, merchant", [
    ("Compra no debito: \"No estabelecimento MERCADO SOL\"", "MERCADO SOL"),
    ("PIX ENVIADO - Cp :12345-MARIA SOUZA", "MARIA SOUZA"),
    ("Pix enviado: \"Cp :60701190-SABESP\"", "SABESP"),
    ("COMPRA CARTAO - COMPRA no estabelecimento IFD*LETICIA", "IFD*LETICIA"),
    ("PAGAMENTO - 123 POSTO", "POSTO"),
    ("NETFLIX", "NETFLIX"),
    ("MERCADOLIVRE PRODUTOS - Parcela 9/12", "MERCADOLIVRE PRODUTOS"),
])
def test_merchant_name(description: str, merchant: str):
    assert ledger.merchant_name(description) == merchant


def test_expenses_are_routine_negative_values(session: Session):
    session.add_all([
        make_transaction("MARKET", -10),
        make_transaction("TRIP HOTEL", -300, context="Trip"),
        make_transaction("ADJUSTED", 0),
        make_transaction("SALARY", 100),
        make_transaction("TRIP REFUND", 20, context="Trip"),
    ])
    session.commit()
    frame = ledger.load(session)

    spent = ledger.expenses(frame)
    earned = ledger.incomes(frame)

    assert spent["description"].tolist() == ["MARKET"]
    assert spent["amount"].tolist() == [10]
    assert earned["description"].tolist() == ["SALARY"]


def test_month_helpers():
    month = pd.Period("2026-03", freq="M")

    assert list(ledger.trailing_months(month, 3).astype(str)) == \
        ["2026-01", "2026-02", "2026-03"]
    assert list(ledger.previous_months(month, 2).astype(str)) == \
        ["2026-01", "2026-02"]


def test_monthly_totals_and_average_ignore_months_without_data(
        session: Session):
    session.add_all([
        make_transaction("A", -10, date=datetime(2026, 1, 5)),
        make_transaction("B", -30, date=datetime(2026, 3, 5)),
        make_transaction("C", 5, date=datetime(2026, 3, 6)),
    ])
    session.commit()
    frame = ledger.load(session)
    months = ledger.month_range(pd.Period("2026-01", freq="M"),
                                pd.Period("2026-03", freq="M"))

    totals = ledger.monthly_totals(ledger.expenses(frame), "amount", months)
    average = ledger.average_over_months_with_data(
        totals, ledger.months_with_data(frame))

    assert totals.tolist() == [10, 0, 30]
    assert average == 20
    assert ledger.average_over_months_with_data(totals.iloc[:0], months) == 0
    assert len(ledger.between(frame, months[1], months[2])) == 2
