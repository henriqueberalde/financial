import pandas

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
