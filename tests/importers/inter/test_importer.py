import hashlib

from pytest import approx
from decimal import Decimal
from pandas import DataFrame
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import financial.database as db
from financial.importers.inter.importer import TransactionsImporter
from financial.models.user import User
from financial.models.category import Category
from financial.models.category_rule import CategoryRule
from financial.importers.inter.model import InterTransaction

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

    monkeypatch.setattr(DataFrame, "to_sql", failing_to_sql)

    importer = TransactionsImporter(session)
    importer.import_from_csv("tests/data/inter_statement.csv")

    assert "Error while saving data to db. data too long" in capsys.readouterr().out  # nopep8
    assert session.query(InterTransaction).count() == 0


def test_inter_importer_replaces_previous_import(session: Session):
    importer = TransactionsImporter(session)

    importer.import_from_csv("tests/data/inter_statement.csv")
    importer.import_from_csv("tests/data/inter_statement.csv")

    assert session.query(InterTransaction).count() == 2


def test_inter_importer_saves_through_a_separate_connection(tmp_path):
    """The statement is written by its own connection, so clearing the
    staging table must be committed first or that insert waits on its lock.
    A file database is used because the in-memory one shares a connection.
    """
    engine = create_engine(f"sqlite:///{tmp_path / 'financial.db'}",
                           connect_args={"timeout": 1})
    db.Base.metadata.create_all(engine)

    with Session(engine) as session:
        importer = TransactionsImporter(session)
        importer.import_from_csv("tests/data/inter_statement.csv")

        assert session.query(InterTransaction).count() == 2

    engine.dispose()


def __sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
