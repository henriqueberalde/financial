import pytest

from collections.abc import Iterator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import financial.entities.db as db

# Mapped classes must be imported so their tables are in db.Base.metadata
import financial.entities.adjustement  # noqa: F401
import financial.entities.inter_transaction  # noqa: F401
import financial.entities.transactions_categories  # noqa: F401


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
