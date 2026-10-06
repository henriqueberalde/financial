import hashlib

from pytest import approx
from decimal import Decimal
from sqlite3 import Timestamp
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

    importer.import_from_csv("tests/test_import.csv")

    transactions = session.query(InterTransaction).all()

    hashed_t0 = __sha256("2019-01-05 00:00:00PAGAMENTO DE CONVENIO - Vivo-233.827566.18")  # nopep8
    hashed_t1 = __sha256("2019-01-06 00:00:00PAGAMENTO DE CONVENIO - Gas-21.537544.65")  # nopep8

    assert len(transactions) == 2

    assert transactions[0].date == Timestamp(2019, 1, 5)
    assert transactions[1].date == Timestamp(2019, 1, 6)

    assert transactions[0].description == "PAGAMENTO DE CONVENIO - Vivo"
    assert transactions[1].description == "PAGAMENTO DE CONVENIO - Gas"

    assert transactions[0].value == approx(Decimal(-233.82))
    assert transactions[1].value == approx(Decimal(-21.53))

    assert transactions[0].balance == approx(Decimal(7566.18))
    assert transactions[1].balance == approx(Decimal(7544.65))

    assert transactions[0].hash == hashed_t0
    assert transactions[1].hash == hashed_t1


def __sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
