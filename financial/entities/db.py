from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base

from financial.settings import database_url


def get_engine(conn_string: str | None = None) -> Engine:
    return create_engine(conn_string or database_url())


def get_session() -> Session:
    return Session(get_engine())


Base = declarative_base()
