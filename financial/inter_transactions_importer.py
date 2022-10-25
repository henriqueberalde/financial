import db
import pandas as pd

from pandas import DataFrame

from financial.user import User

BANK = "077"


class InterTransactionsImporter:
    def __init__(self, user) -> None:
        self.df: DataFrame
        self.user: User = user
        self.file_path: str

    def import_from_csv(self, file_path: str) -> None:
        self.file_path = file_path

        df_local = self.__load_csv()

        if (df_local is None):
            return None

        self.df = df_local
        self.__normalize_df()

        return self.__save_df()

    def __load_csv(self) -> DataFrame | None:
        try:
            self.df = pd.read_csv(
                filepath_or_buffer=self.file_path,
                sep=";",
                header=4,
                names=["date", "description", "value", "balance"],
                decimal=",",
                thousands=".")

            print('\nReading File')
            print(f'{self.file_path}')

            return self.df
        except Exception as e:
            print(f'Error while reading csv {self.file_path}. {e}')
            return None

    def __normalize_df(self) -> DataFrame:
        print(f'\nNormalizing data. {len(self.df)} rows.')

        self.df.insert(0, "user_id", self.user.id)
        self.df.insert(1, "user_account", self.user.account)
        self.df.insert(2, "bank", BANK)
        self.df['date'] = pd.to_datetime(self.df['date'], format='%d/%m/%Y')

        print(f'First 5 lines of {len(self.df)}:')
        print(self.df.head())

        return self.df

    def __save_df(self) -> None:
        engine = db.get_engine()
        mysql_connection = engine.connect()

        try:
            self.df.to_sql(name='transactions',
                           con=mysql_connection,
                           if_exists='append',
                           index=False)
        except Exception as e:
            print(f'Error while save data to db. {e}')
        finally:
            mysql_connection.close()
