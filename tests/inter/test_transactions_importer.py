import hashlib

from pytest import approx
from decimal import Decimal
from pandas import DataFrame as PandasDataFrame
from datetime import datetime
from sqlalchemy.orm import Session
from financial.inter.transactions_importer import TransactionsImporter
from financial.entities.user import User
from financial.entities.category import Category
from financial.entities.category_rule import CategoryRule
from financial.entities.inter_transaction import InterTransaction

user = User(id=1, account="123")


def test_inter_importer(session: Session):
    importer = TransactionsImporter(session)

    vivo = Category(name="Vivo")
    vivo_rule = CategoryRule(category=vivo, rule="vivo")

    gas = Category(name="Gas")
    gas_rule = CategoryRule(category=gas, rule="gas")

    session.add(vivo)
    session.add(vivo_rule)
    session.add(gas)
    session.add(gas_rule)
    session.commit()

    importer.import_from_csv("tests/data/inter_statement.csv")

    transactions = session.query(InterTransaction).all()

    hashed_t0 = __sha256("2019-01-05 00:00:00PAGAMENTO DE CONVENIO - Vivo-233.827566.18")  # nopep8
    hashed_t1 = __sha256("2019-01-06 00:00:00PAGAMENTO DE CONVENIO - Gas-21.537544.65")  # nopep8

    assert len(transactions) == 2

    assert transactions[0].date == datetime(2019, 1, 5)
    assert transactions[1].date == datetime(2019, 1, 6)

    assert transactions[0].description == "PAGAMENTO DE CONVENIO - Vivo"
    assert transactions[1].description == "PAGAMENTO DE CONVENIO - Gas"

    assert transactions[0].value == approx(Decimal(-233.82))
    assert transactions[1].value == approx(Decimal(-21.53))

    assert transactions[0].balance == approx(Decimal(7566.18))
    assert transactions[1].balance == approx(Decimal(7544.65))

    assert transactions[0].hash == hashed_t0
    assert transactions[1].hash == hashed_t1


def test_inter_importer_reports_missing_file(session: Session, capsys):
    TransactionsImporter(session).import_from_csv("tests/missing.csv")

    assert "Error." in capsys.readouterr().out
    assert session.query(InterTransaction).count() == 0


def test_inter_importer_reports_save_errors(session: Session,
                                            monkeypatch,
                                            capsys):
    def failing_to_sql(*args, **kwargs):
        raise RuntimeError("data too long")

    monkeypatch.setattr(PandasDataFrame, "to_sql", failing_to_sql)

    importer = TransactionsImporter(session)
    importer.import_from_csv("tests/data/inter_statement.csv")

    assert "Error while saving data to db. data too long" in capsys.readouterr().out  # nopep8
    assert session.query(InterTransaction).count() == 0


def test_inter_importer_replaces_previous_import(session: Session):
    session.add(CategoryRule(category=Category(name="Vivo"), rule="vivo"))
    session.commit()
    importer = TransactionsImporter(session)

    importer.import_from_csv("tests/data/inter_statement.csv")
    importer.import_from_csv("tests/data/inter_statement.csv")

    assert session.query(InterTransaction).count() == 2
    assert len(importer.category_rules) == 1


def __sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
