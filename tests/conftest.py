import pytest
import financial.entities.db as db
from sqlalchemy.orm import Session

from financial.entities.user import User
from financial.inter.transactions_importer import TransactionsImporter

__session = Session(db.get_engine("mysql+pymysql://financial_test:pass123@localhost/financial_test"))  # nopep8


@pytest.fixture()
def session(scope="function") -> Session:
    __session.expunge_all()
    __session.execute("DELETE FROM transactions_categories;")
    __session.execute("DELETE FROM transactions;")
    __session.execute("DELETE FROM category_rules;")
    __session.execute("DELETE FROM categories;")

    __session.execute("ALTER TABLE transactions AUTO_INCREMENT = 1;")
    __session.execute("ALTER TABLE category_rules AUTO_INCREMENT = 1;")
    __session.execute("ALTER TABLE categories AUTO_INCREMENT = 1;")
    __session.commit()

    return __session  # nopep8


@pytest.fixture(scope="function")
def interImporterUser1():
    """
    Instance of Inter`s TransactionsImporter with id:1, account: user_account
    """
    return TransactionsImporter(session(), User(1, "user_account"))
