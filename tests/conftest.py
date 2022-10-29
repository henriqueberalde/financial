import pytest
import financial.entities.db as db
from sqlalchemy.orm import Session

from financial.entities.user import User
from financial.inter.transactions_importer import TransactionsImporter


def __session() -> Session:
    return Session(db.get_engine("mysql+pymysql://financial_test:pass123@localhost/financial_test"))  # nopep8


@pytest.fixture()
def session(scope="session") -> Session:
    session = __session()

    session.execute("DELETE FROM transactions;")
    session.execute("ALTER TABLE transactions AUTO_INCREMENT = 1;")
    session.execute("DELETE FROM category_rules;")
    session.execute("ALTER TABLE category_rules AUTO_INCREMENT = 1;")
    session.execute("DELETE FROM categories;")
    session.execute("ALTER TABLE categories AUTO_INCREMENT = 1;")
    session.commit()

    return session  # nopep8


@pytest.fixture(scope="function")
def interImporterUser1():
    """
    Instance of Inter`s TransactionsImporter with id:1, account: user_account
    """
    return TransactionsImporter(__session(), User(1, "user_account"))
