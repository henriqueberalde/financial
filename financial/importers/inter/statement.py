from pandas import DataFrame, to_datetime
from financial.importers.inter.constants import CSV_DATE_FORMAT
from financial.hashing import transaction_hash


class Statement:
    def __init__(self, data_frame: DataFrame):
        self.data_frame = data_frame

    def normalize_date(self) -> None:
        self.data_frame['date'] = to_datetime(
            self.data_frame['date'], format=CSV_DATE_FORMAT)

    def add_hash_column(self) -> None:
        self.data_frame['hash'] = [
            transaction_hash(row["date"],
                             row["description"],
                             f"{float(row['value']):.2f}",
                             f"{row['balance']:.2f}")
            for _, row in self.data_frame.iterrows()
        ]
