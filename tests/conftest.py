import pytest

from financial.user import User
from financial.inter_transactions_importer import InterTransactionsImporter


@pytest.fixture(scope="module")
def interImporterUser1():
    """
    Instance of InterTransactionsImporter with id:1, account: user_account
    """
    return InterTransactionsImporter(User(1, "user_account"))
