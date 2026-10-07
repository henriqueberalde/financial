import shutil

from datetime import datetime
from decimal import Decimal

import pytest

from click.testing import CliRunner, Result
from sqlalchemy.orm import Session

import financial.database as db

from factories import make_transaction

from financial.cli import cli, main, print_category_conflicts
from financial.importers.inter_credit_card.model import \
    InterCreditCardTransaction
from financial.models.adjustment import Adjustment
from financial.models.category import Category
from financial.models.category_rule import CategoryRule
from financial.importers.inter.model import InterTransaction
from financial.models.transaction import Transaction
from financial.models.transaction_category import TransactionCategory


@pytest.fixture(autouse=True)
def cli_session(session: Session, monkeypatch) -> Session:
    monkeypatch.setattr(db, "get_session", lambda: session)
    return session


def invoke(*args: str) -> Result:
    result = CliRunner().invoke(cli, list(args))

    assert result.exception is None, result.output
    assert result.exit_code == 0
    return result


def test_inter_import_statement(session: Session):
    invoke("inter-import-statement", "-f", "tests/data/inter_statement.csv")

    assert session.query(InterTransaction).count() == 2


def test_merge_inter_transactions_merges_and_categorizes(session: Session):
    vivo = Category(name="Vivo")
    session.add(CategoryRule(category=vivo, rule="vivo"))
    session.commit()
    invoke("inter-import-statement", "-f", "tests/data/inter_statement.csv")

    result = invoke("merge-inter-transactions",
                    "-user_id", "1", "-user_account", "123")

    transactions = session.query(Transaction).order_by(Transaction.id).all()
    assert len(transactions) == 2
    assert transactions[0].category_id == vivo.id
    assert transactions[1].category_id is None
    assert "done" in result.output


def test_set_context(session: Session):
    first, second, third = __add_transactions(session, 3)

    invoke("set-context", "-c", "Trip", "-ids", f"{first.id} {third.id}")

    session.expire_all()
    assert [first.context, second.context, third.context] == \
        ["Trip", None, "Trip"]


def test_create_category(session: Session):
    invoke("create-category", "-name", "Gas", "-sector", "1 Essential")

    category = session.query(Category).one()
    assert (category.name, category.sector) == ("Gas", "1 Essential")


def test_set_category(session: Session):
    category = Category(name="Gas")
    session.add(category)
    transaction, = __add_transactions(session, 1)

    invoke("set-category", "-category_name", "Gas",
           "-transaction_id", str(transaction.id))

    assert session.query(TransactionCategory).count() == 1
    assert session.get(Transaction, transaction.id).category_id == \
        category.id


def test_create_category_rule_categorizes_transactions(session: Session):
    category = Category(name="Gas")
    session.add(category)
    transaction, = __add_transactions(session, 1, "AUTO POSTO")

    invoke("create-category-rule", "-category_name", "Gas",
           "-rule", "posto")

    assert session.query(CategoryRule).one().rule == "posto"
    assert session.get(Transaction, transaction.id).category_id == \
        category.id


def test_create_category_rule_reports_conflicts(session: Session):
    session.add(CategoryRule(category=Category(name="Water"), rule="agua"))
    session.add(Category(name="Gas"))
    transaction, = __add_transactions(session, 1, "POSTO CARAGUATATUBA")

    result = invoke("create-category-rule", "-category_name", "Gas",
                    "-rule", "posto")

    assert "1 transactions skipped (category conflict):" in result.output
    assert session.get(Transaction, transaction.id).category_id is None


def test_adjust(session: Session):
    spend, gain = __add_transactions(session, 2)
    spend.value = -30  # type: ignore
    gain.value = 30  # type: ignore
    session.commit()

    invoke("adjust", "-reason", "Refund",
           "-transactions", f"{spend.id} {gain.id}")

    assert session.query(Adjustment).one().reason == "Refund"
    assert (spend.value, gain.value) == (0, 0)


def test_print_category_conflicts_prints_nothing_without_conflicts(capsys):
    print_category_conflicts([])

    assert capsys.readouterr().out == ""


def test_inter_credit_card_import_stages_every_invoice(session: Session,
                                                       tmp_path):
    for name in ["2024-06.csv", "2024-07.csv"]:
        shutil.copy(f"tests/data/inter_credit_card/{name}", tmp_path / name)
    (tmp_path / "fatura-2024-08.csv").touch()

    result = invoke("inter-credit-card-import", "-d", str(tmp_path))

    assert "2024-06.csv: 5 lines staged" in result.output
    assert "2024-07.csv: 1 lines staged" in result.output
    assert "fatura-2024-08.csv: not imported." in result.output
    assert session.query(InterCreditCardTransaction).count() == 6


def test_inter_credit_card_import_without_files(tmp_path):
    result = invoke("inter-credit-card-import", "-d", str(tmp_path))

    assert f"No invoice files found in {tmp_path}" in result.output


def test_inter_credit_card_merge_reports_each_month(session: Session):
    category = Category(name="Mercado")
    session.add(CategoryRule(category=category, rule="mercado exemplo"))
    payment = make_transaction(
        'Pagamento efetuado: "Debito Automatico Fatura Cartao Inter"',
        Decimal("-1200.00"),
        date=datetime(2024, 6, 12))
    session.add(payment)
    session.commit()
    invoke("inter-credit-card-import", "-d", "tests/data/inter_credit_card")

    result = invoke("inter-credit-card-merge",
                    "-user_id", "1", "-user_account", "123")

    assert ("2024-06: 5 transactions merged, R$ 1186.96 deducted from the "
            "card payment") in result.output
    assert "2024-07: not merged, kept staged." in result.output
    assert payment.value == Decimal("-13.04")
    market = session.query(Transaction).filter(
        Transaction.description == "MERCADO EXEMPLO SAO PAULO BRA").one()
    assert market.category_id == category.id


def test_main_registers_repl_and_runs_cli(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["financial", "--help"])

    with pytest.raises(SystemExit) as exit_info:
        main()

    assert exit_info.value.code == 0
    assert "repl" in capsys.readouterr().out


def __add_transactions(session: Session,
                       count: int,
                       description: str = "transaction") -> list[Transaction]:
    transactions = [make_transaction(f"{description} {index}")
                    for index in range(count)]
    session.add_all(transactions)
    session.commit()

    return transactions


def test_dashboard_serves_the_app(monkeypatch):
    served = {}
    monkeypatch.setattr("financial.cli.uvicorn.run",
                        lambda app, host, port: served.update(
                            app=app, host=host, port=port))
    monkeypatch.setenv("DASHBOARD_PORT", "9000")

    invoke("dashboard")

    assert served["port"] == 9000
    assert served["app"].title == "financial"
