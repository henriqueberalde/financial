import db
from typing import Iterable, List
import numpy as np


class Transaction:
    @staticmethod
    def set_context_of_many(ids: str, context: str) -> None:
        Transaction.__set_column_of_many("context", ids, context)

    @staticmethod
    def set_category_of_many(ids: str, category: str) -> None:
        Transaction.__set_column_of_many("category", ids, category)

    @staticmethod
    def __set_column_of_many(column: str,
                             ids: Iterable | str,
                             column_parm: str) -> None:
        engine = db.get_engine()
        mysql_connection = engine.connect()

        try:
            ids_param = ""
            if not isinstance(ids, str):
                ids_list_str = np.array(np.array(map(str, ids))).tolist()
                ids_param = ", ".join(ids_list_str)
            else:
                ids_param = ids

            mysql_connection.exec_driver_sql(
                f"UPDATE transactions SET {column}=%(column_parm)s " +
                f"where id IN({ids_param});", {"column_parm": column_parm})

        except Exception as e:
            print(f"Error while save data to db.{e}")
        finally:
            mysql_connection.close()
