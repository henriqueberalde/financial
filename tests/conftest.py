import pytest
import financial.entities.db as db
from sqlalchemy.orm import Session

from financial.entities.user import User
from financial.inter.transactions_importer import TransactionsImporter


def __session() -> Session:
    return Session(db.get_engine("mysql+pymysql://financial_test:pass123@localhost/financial_test"))  # nopep8


@pytest.fixture()
def session(scope="function") -> Session:
    session = __session()
    session.expire_all()
    session.expunge_all()

    session.execute("DELETE FROM transactions;")
    session.execute("DELETE FROM category_rules;")
    session.execute("DELETE FROM categories;")

    return session


@pytest.fixture(scope="function")
def interImporterUser1():
    """
    Instance of Inter`s TransactionsImporter with id:1, account: user_account
    """
    return TransactionsImporter(__session(), User(1, "user_account"))
