import financial.entities.db as db
import pandas as pd

from financial.base_transactions_importer import BaseTransactionsImporter
from pandas import DataFrame as PandasDataFrame
from financial.inter.data_frame import DataFrame as InterDataFrame
from financial.entities.category import Category
from financial.entities.category_rule import CategoryRule
from financial.entities.normalization_error import NormalizationError
from financial.entities.user import User


class TransactionsImporter(BaseTransactionsImporter):
    def __init__(self, user) -> None:
        super().__init__("077")

        self.data_frame: InterDataFrame
        self.user: User = user
        self.file_path: str
        self.category_rules: list[CategoryRule] = []
        self.errors_messages: list[str] = []

    def import_from_csv(self, file_path: str) -> None:
        self.file_path = file_path

        try:
            print('\nReading File')
            print(f'{self.file_path}')
            pandas_data_frame = self.__load_csv()

            if (pandas_data_frame is None):
                print('\nEmpty file, nothing was loaded')
                return None

            self.data_frame = InterDataFrame(pandas_data_frame,
                                             self.category_rules)

            print(f'\nNormalizing Data')
            self.data_frame.normalize_date()
            self.data_frame.add_fixed_columns(self.user, self.bank)

            print('Fetching category rules')
            self.__fetch_category_rules()
            self.data_frame.set_category_by_rules()

            self.__save_df()

        except NormalizationError as e:
            print(f'\nNormalizing Errors. \n\n{e}')
            return None
        except Exception as e:
            print(f'\nError. \n\n{e}')
            return None

    def __load_csv(self) -> PandasDataFrame | None:
        df = pd.read_csv(
            filepath_or_buffer=self.file_path,
            sep=";",
            header=4,
            names=["date", "description", "value", "balance"],
            decimal=",",
            thousands=".")

        return df

    def __save_df(self) -> None:
        engine = db.get_engine()
        mysql_connection = engine.connect()

        try:
            self.data_frame.data_frame.to_sql(name='transactions',
                                              con=mysql_connection,
                                              if_exists='append',
                                              index=False)
        except Exception as e:
            print(f'Error while saving data to db. {e}')
        finally:
            mysql_connection.close()

    def __fetch_category_rules(self):
        if len(self.category_rules) == 0:
            self.category_rules = CategoryRule.get_all()
