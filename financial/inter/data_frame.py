import pandas

from pandas import DataFrame as PandasDataFrame
from financial.constants import INTER_CSV_DATE_FORMAT
from financial.entities.category_rule import CategoryRule
from financial.hashing import transaction_hash


class DataFrame:
    def __init__(self,
                 data_frame: PandasDataFrame,
                 category_rules: list[CategoryRule]):

        self.data_frame = data_frame
        self.category_rules = category_rules

    def normalize_date(self) -> None:
        self.data_frame['date'] = pandas.to_datetime(
            self.data_frame['date'], format=INTER_CSV_DATE_FORMAT)

    def add_hash_column(self) -> None:
        self.data_frame['hash'] = [
            transaction_hash(row["date"],
                             row["description"],
                             f"{float(row['value']):.2f}",
                             f"{row['balance']:.2f}")
            for _, row in self.data_frame.iterrows()
        ]
