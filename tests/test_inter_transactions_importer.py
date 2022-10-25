from financial.inter_transactions_importer import InterTransactionsImporter
from financial.user import User
from pandas import Timestamp


def test_importer_init(interImporterUser1):
    assert interImporterUser1.user.id == 1
    assert interImporterUser1.user.account == "user_account"


def test_import_csv_normalize_data(interImporterUser1):
    interImporterUser1.import_from_csv("tests/test_import.csv")
    assert interImporterUser1.df["user_id"][0] == 1
    assert interImporterUser1.df["user_account"][0] == "user_account"
    assert interImporterUser1.df["bank"][0] == "077"
    assert interImporterUser1.df["date"][0] == Timestamp("2019-01-04 00:00:00")


def test_import_csv_df_qty(interImporterUser1):
    assert len(interImporterUser1.df.index) == 3


def test_import_csv_df_date(interImporterUser1):
    assert interImporterUser1.df["date"][0] == Timestamp("2019-01-04 00:00:00")
    assert interImporterUser1.df["date"][1] == Timestamp("2019-01-05 00:00:00")
    assert interImporterUser1.df["date"][2] == Timestamp("2019-01-06 00:00:00")


def test_import_csv_df_value(interTransactionsImporterUser1):
    assert interTransactionsImporterUser1.df["value"][0] == 7800.0
    assert interTransactionsImporterUser1.df["value"][1] == -233.82
    assert interTransactionsImporterUser1.df["value"][2] == -21.53
