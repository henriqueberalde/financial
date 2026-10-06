import pytest

from collections.abc import Iterator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import financial.database as db

# Importing the packages registers every table in db.Base.metadata
import financial.importers.inter  # noqa: F401
import financial.models  # noqa: F401


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
