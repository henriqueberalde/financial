import pytest

from financial.entities.user import User
from financial.inter.transactions_importer import TransactionsImporter


@pytest.fixture(scope="function")
def interImporterUser1():
    """
    Instance of Inter`s TransactionsImporter with id:1, account: user_account
    """
    return TransactionsImporter(User(1, "user_account"))
