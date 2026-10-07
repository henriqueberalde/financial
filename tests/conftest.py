import pandas as pd
import pytest

from collections.abc import Callable, Iterator
from datetime import datetime
from typing import Any
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import financial.database as db

# Importing the packages registers every table in db.Base.metadata
import financial.importers.inter  # noqa: F401
import financial.importers.inter_credit_card  # noqa: F401
import financial.models  # noqa: F401

from factories import make_transaction
from financial.models.category import Category
from financial.models.transaction import Transaction
from financial.services.analytics import ledger


@pytest.fixture()
def session() -> Iterator[Session]:
    """Session bound to a new in-memory SQLite database for each test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    db.Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    engine.dispose()


@pytest.fixture()
def add(session: Session):
    """Add a transaction on the given ISO day, creating its category (by
    name) on first use, and return it."""
    categories: dict[str, Category] = {}

    def add_transaction(day: str,
                        description: str,
                        value: float,
                        category: str | None = None,
                        sector: str = "Essential",
                        **fields: Any) -> Transaction:
        if category is not None and category not in categories:
            categories[category] = Category(name=category, sector=sector)
        transaction = make_transaction(
            description, value, date=datetime.fromisoformat(day),
            category=categories.get(category), **fields)
        session.add(transaction)
        session.commit()
        return transaction

    return add_transaction


@pytest.fixture()
def load(session: Session) -> Callable[[], pd.DataFrame]:
    """Load the analytics ledger of the test database."""
    return lambda: ledger.load(session)
