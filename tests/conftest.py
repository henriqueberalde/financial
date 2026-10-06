import pytest
import financial.entities.db as db
from sqlalchemy import text
from sqlalchemy.orm import Session


import logging

# not sure how to 'bind' to the logger in __main__.py

__session = Session(db.get_engine("mysql+pymysql://financial_test:pass123@localhost/financial_test"))  # nopep8
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


@pytest.fixture()
def session(scope="function") -> Session:
    __session.expunge_all()
    __session.execute(text("DELETE FROM transactions_categories;"))
    __session.execute(text("DELETE FROM transactions_adjustments;"))
    __session.execute(text("DELETE FROM adjustments;"))
    __session.execute(text("DELETE FROM transactions;"))
    __session.execute(text("DELETE FROM inter_transactions;"))
    __session.execute(text("DELETE FROM category_rules;"))
    __session.execute(text("DELETE FROM categories;"))

    __session.execute(text("ALTER TABLE transactions AUTO_INCREMENT = 1;"))
    __session.execute(text("ALTER TABLE transactions_adjustments AUTO_INCREMENT = 1;"))  # nopep8
    __session.execute(text("ALTER TABLE adjustments AUTO_INCREMENT = 1;"))
    __session.execute(text("ALTER TABLE inter_transactions AUTO_INCREMENT = 1;"))  # nopep8
    __session.execute(text("ALTER TABLE category_rules AUTO_INCREMENT = 1;"))
    __session.execute(text("ALTER TABLE categories AUTO_INCREMENT = 1;"))
    __session.commit()

    return __session  # nopep8
