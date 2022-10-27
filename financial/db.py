from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base


def get_engine() -> Engine:
    return create_engine("mysql+pymysql://" +
                         "financial:pass123@localhost/financial")


Base = declarative_base(get_engine())


def get_session() -> Session:
    return Session(get_engine())
