import pandas
import hashlib
import pandas as pd

from datetime import datetime
from pandas import DataFrame as PandasDataFrame
from financial.entities.category_rule import CategoryRule


class DataFrame:
    def __init__(self,
                 data_frame: PandasDataFrame,
                 category_rules: list[CategoryRule]):

        self.data_frame = data_frame
        self.category_rules = category_rules

    def normalize_date(self) -> None:
        self.data_frame['date'] = pandas.to_datetime(self.data_frame['date'],
                                                     format='%d/%m/%Y')

    def add_hash_column(self) -> None:
        list_concat_string = []

        for index, row in self.data_frame.iterrows():
            date = row["date"].strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            description = row["description"]
            value = float(row["value"])
            balance = row["balance"]

            s = f"{date}{description}{value:.2f}{balance:.2f}"
            list_concat_string.append(s)

        self.data_frame['hash'] = list_concat_string
        self.data_frame['hash'] = self.data_frame['hash'].apply(
            DataFrame.to_hash)

    @staticmethod
    def to_hash(s):
        hash = hashlib.sha256(s.encode('utf-8')).hexdigest()

        return hash
