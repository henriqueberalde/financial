from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

import financial.entities.db as db


def test_get_engine_uses_given_connection_string():
    engine = db.get_engine("sqlite://")

    assert isinstance(engine, Engine)
    assert str(engine.url) == "sqlite://"


def test_get_session_is_bound_to_application_engine(monkeypatch):
    engine = create_engine("sqlite://")
    monkeypatch.setattr(db, "get_engine", lambda: engine)

    assert db.get_session().get_bind() is engine


def test_get_engine_defaults_to_database_url_setting(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite://")

    assert str(db.get_engine().url) == "sqlite://"
