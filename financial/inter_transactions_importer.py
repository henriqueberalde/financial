import db
import re
import pandas as pd

from pandas import DataFrame
from financial.category import Category
from financial.category_rule import CategoryRule
from financial.normalize_error import NormalizeError
from financial.user import User

BANK = "077"


class InterTransactionsImporter:
    def __init__(self, user) -> None:
        self.df: DataFrame
        self.user: User = user
        self.file_path: str
        self.rules: list[CategoryRule] = []
        self.errors_messages: list[str] = []

    def import_from_csv(self, file_path: str) -> None:
        self.file_path = file_path
        self.errors_messages = []

        try:
            df_local = self.__load_csv()

            if (df_local is None):
                return None

            self.df = df_local
            self.__normalize_df()

            if (len(self.errors_messages)):
                raise NormalizeError(self.errors_messages)

            self.__save_df()

        except NormalizeError as e:
            print(f'\nNormalizing Errors. \n\n{str(e)}')
            return None
        except Exception as e:
            print(f'Error. {e}')
            return None

    def __load_csv(self) -> DataFrame | None:
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

    def __normalize_df(self) -> DataFrame:
        print(f'\nNormalizing data. {len(self.df)} rows.')

        self.df.insert(0, "user_id", self.user.id)
        self.df.insert(1, "user_account", self.user.account)
        self.df.insert(2, "bank", BANK)
        self.df['date'] = pd.to_datetime(self.df['date'], format='%d/%m/%Y')
        self.df['category_id'] = self.df['description'].apply(
            self.__set_category
        )

        print(f'First 5 lines of {len(self.df)}:')
        print(self.df.head())

        return self.df

    def __set_category(self, description: str) -> int | None:
        self.__update_rules()
        matched_rules: list[CategoryRule] = []

        for rule in self.rules:
            if re.search(str(rule.rule),
                         description,
                         re.IGNORECASE) is not None:
                matched_rules.append(rule)

        if len(matched_rules) == 1:
            return int(str(matched_rules[0].category_id))
        elif len(matched_rules) == 0:
            return None
        else:
            matched_categories = list(
                [rule.category.name for rule in matched_rules])

            if self.__has_diferent_str(matched_categories):
                self.errors_messages.append("More than one category match. " +
                                            f"Description: '{description}', " +
                                            f"Matches: {matched_categories}")
            else:
                return int(str(matched_rules[0].category_id))

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

    def __update_rules(self) -> None:
        if len(self.rules) <= 0:
            self.rules = db.get_session().query(CategoryRule).all()

    def __has_diferent_str(self, str_list: list[str]) -> bool:
        prev_str: str | None = None
        for s in str_list:
            if prev_str is None:
                prev_str = s

            if prev_str != s:
                return True

        return False
