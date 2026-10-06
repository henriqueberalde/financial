from sqlalchemy.orm import Session
from financial.importers.base import BaseTransactionsImporter
from financial.importers.inter import constants
from pandas import DataFrame, read_csv
from financial.importers.inter.statement import Statement
from financial.importers.inter import staging


class TransactionsImporter(BaseTransactionsImporter):
    def __init__(self, session: Session) -> None:
        super().__init__(constants.BANK_CODE)

        self.session = session
        self.statement: Statement
        self.file_path: str

    def import_from_csv(self, file_path: str) -> None:
        self.file_path = file_path

        try:
            print('\nCleaning up inter_transactions')
            staging.clear(self.session)

            print('\nReading File')
            print(f'{self.file_path}')
            pandas_data_frame = self.__load_csv()

            print(f'{len(pandas_data_frame.index)} transactions found on csv file')  # nopep8

            self.statement = Statement(pandas_data_frame)

            print('\nNormalizing Data')
            self.statement.normalize_date()
            self.statement.add_hash_column()

            print(self.statement.data_frame)

            print('\nSaving...')
            self.__save_df()

        except Exception as e:
            print(f'\nError. \n\n{e}')
            return None

    def __load_csv(self) -> DataFrame:
        df = read_csv(
            filepath_or_buffer=self.file_path,
            sep=constants.CSV_SEPARATOR,
            header=constants.CSV_HEADER_ROW,
            names=constants.CSV_COLUMNS,
            decimal=constants.CSV_DECIMAL,
            thousands=constants.CSV_THOUSANDS)

        return df

    def __save_df(self) -> None:
        engine = self.session.get_bind()
        mysql_connection = engine.connect()

        try:
            self.statement.data_frame.to_sql(name='inter_transactions',
                                             con=mysql_connection,
                                             if_exists='append',
                                             index=False)
        except Exception as e:
            print(f'Error while saving data to db. {e}')
        finally:
            self.session.commit()
