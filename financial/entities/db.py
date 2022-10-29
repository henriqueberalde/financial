from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base


def get_engine(conn_string: str = "mysql+pymysql://financial:pass123@localhost/financial") -> Engine:  # nopep8
    return create_engine(conn_string)


def get_session() -> Session:
    return Session(get_engine())


Base = declarative_base(get_engine())
