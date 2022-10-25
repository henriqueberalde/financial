from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def get_engine() -> Engine:
    return create_engine("mysql+pymysql://" +
                         "financial:pass123@localhost/financial")
