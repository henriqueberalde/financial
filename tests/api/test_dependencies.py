from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import financial.database as db

from financial.api import dependencies


def test_sessions_share_one_engine(monkeypatch):
    engines = []
    monkeypatch.setattr(db, "get_engine",
                        lambda: engines.append(create_engine("sqlite://"))
                        or engines[-1])
    dependencies.engine.cache_clear()

    sessions = [next(dependencies.get_session()) for _ in range(2)]

    assert all(isinstance(session, Session) for session in sessions)
    assert len(engines) == 1
    dependencies.engine.cache_clear()
