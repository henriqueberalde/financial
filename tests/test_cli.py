import pytest

from click.testing import CliRunner, Result
from sqlalchemy.orm import Session

import financial.entities.db as db

from factories import make_transaction

from financial.cli import cli, print_category_conflicts
from financial.entities.adjustement import Adjustment
from financial.entities.category import Category
from financial.entities.category_rule import CategoryRule
from financial.entities.inter_transaction import InterTransaction
from financial.entities.transaction import Transaction
from financial.entities.transactions_categories import TransactionsCategories


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
    invoke("inter-import-statement", "-f", "tests/test_import.csv")

    assert session.query(InterTransaction).count() == 2


def test_merge_inter_transactions_merges_and_categorizes(session: Session):
    vivo = Category(name="Vivo")
    session.add(CategoryRule(category=vivo, rule="vivo"))
    session.commit()
    invoke("inter-import-statement", "-f", "tests/test_import.csv")

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

    assert session.query(TransactionsCategories).count() == 1
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


def __add_transactions(session: Session,
                       count: int,
                       description: str = "transaction") -> list[Transaction]:
    transactions = [make_transaction(f"{description} {index}")
                    for index in range(count)]
    session.add_all(transactions)
    session.commit()

    return transactions
