import pytest

from financial.inter.data_frame import DataFrame
from pandas import DataFrame as PandasDataFrame
from pandas import Timestamp
from financial.entities.user import User
from financial.entities.category_rule import CategoryRule
from financial.entities.category import Category
from financial.entities.normalization_error import NormalizationError


bank = "077"
category_rules = [
    CategoryRule(category=Category(id=1, name="Category1"), rule="category1"),
    CategoryRule(category=Category(id=2, name="Category2"), rule="category2"),
]
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


def test_add_fixed_columns():
    inter_data_frame = DataFrame(simple_pandas_data_frame, [])
    user = User(1, "user_account1")

    inter_data_frame.add_fixed_columns(user, bank)

    assert inter_data_frame.data_frame["user_id"][0] == user.id
    assert inter_data_frame.data_frame["user_account"][0] == user.account
    assert inter_data_frame.data_frame["bank"][0] == bank


def test_set_category_by_rules():
    category_data_frame = PandasDataFrame([
        {
            "date": "05/01/2019",
            "description": "PAGAMENTO DE CONVENIO - category1",
            "value": -233.82,
            "balance": 7566.18,
        },
        {
            "date": "05/01/2019",
            "description": "PAGAMENTO DE CONVENIO - category2",
            "value": -233.82,
            "balance": 7566.18,
        },
        {
            "date": "05/01/2019",
            "description": "PAGAMENTO DE CONVENIO - Nao categorizado",
            "value": -233.82,
            "balance": 7566.18,
        },
    ])
    inter_data_frame = DataFrame(category_data_frame, category_rules)

    inter_data_frame.set_category_by_rules()

    assert inter_data_frame.data_frame["category_id"][0] == "1"
    assert inter_data_frame.data_frame["category_id"][1] == "2"
    assert inter_data_frame.data_frame["category_id"][2] is None


def test_set_category_by_rules_many_matched_categories():
    with pytest.raises(
            NormalizationError,
            match="More than one category match\\. " +
                  "Description: 'category1 category2', " +
                  "Matches: \\['Category1', 'Category2'\\]"
            ):

        category_data_frame = PandasDataFrame([
            {
                "date": "05/01/2019",
                "description": "category1 category2",
                "value": -233.82,
                "balance": 7566.18,
            }
        ])

        inter_data_frame = DataFrame(category_data_frame, category_rules)
        inter_data_frame.set_category_by_rules()


def test_set_category_by_rules_many_category_conflict_errors():
    with pytest.raises(NormalizationError) as e_info:

        category_data_frame = PandasDataFrame([
            {
                "date": "05/01/2019",
                "description": "1 category1 category2",
                "value": -233.82,
                "balance": 7566.18,
            },
            {
                "date": "05/01/2019",
                "description": "2 category1 category2",
                "value": -233.82,
                "balance": 7566.18,
            }
        ])

        inter_data_frame = DataFrame(category_data_frame, category_rules)
        inter_data_frame.set_category_by_rules()

    assert e_info.value.messages[0] == "More than one category match. Description: '1 category1 category2', Matches: ['Category1', 'Category2']"  # nopep8
    assert e_info.value.messages[1] == "More than one category match. Description: '2 category1 category2', Matches: ['Category1', 'Category2']"  # nopep8
