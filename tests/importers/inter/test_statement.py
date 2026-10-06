import hashlib

from financial.importers.inter.statement import Statement
from pandas import DataFrame
from pandas import Timestamp


simple_pandas_data_frame = DataFrame(
        {
            "date": "05/01/2019",
            "description": "PAGAMENTO DE CONVENIO - Vivo",
            "value": -233.82,
            "balance": 7566.18,
        }, index=[0]
    )


def test_normalize_date():
    statement = Statement(simple_pandas_data_frame, [])
    statement.normalize_date()
    assert statement.data_frame["date"][0] == Timestamp(
        "2019-01-05 00:00:00")


def test_add_hash_column_formats_values_with_two_decimals():
    statement = Statement(DataFrame({
        "date": ["05/01/2019"],
        "description": ["PAGAMENTO DE CONVENIO - Vivo"],
        "value": [-233.8],
        "balance": [7566],
    }), [])
    statement.normalize_date()

    statement.add_hash_column()

    assert statement.data_frame["hash"][0] == hashlib.sha256(
        b"2019-01-05 00:00:00PAGAMENTO DE CONVENIO - Vivo-233.807566.00"
    ).hexdigest()
