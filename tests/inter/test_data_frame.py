from financial.inter.data_frame import DataFrame
from pandas import DataFrame as PandasDataFrame
from pandas import Timestamp


simple_pandas_data_frame = PandasDataFrame(
        {
            "date": "05/01/2019",
            "description": "PAGAMENTO DE CONVENIO - Vivo",
            "value": -233.82,
            "balance": 7566.18,
        }, index=[0]
    )


def test_normalize_date():
    inter_data_frame = DataFrame(simple_pandas_data_frame, [])
    inter_data_frame.normalize_date()
    assert inter_data_frame.data_frame["date"][0] == Timestamp(
        "2019-01-05 00:00:00")
