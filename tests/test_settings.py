import pytest

from financial import settings

VARIABLE = "FINANCIAL_TEST_VARIABLE"


def test_get_env_returns_environment_value(monkeypatch):
    monkeypatch.setenv(VARIABLE, "value")

    assert settings.get_env(VARIABLE) == "value"


def test_get_env_returns_default_when_unset(monkeypatch):
    monkeypatch.delenv(VARIABLE, raising=False)

    assert settings.get_env(VARIABLE, "default") == "default"


def test_get_env_raises_when_unset_without_default(monkeypatch):
    monkeypatch.delenv(VARIABLE, raising=False)

    with pytest.raises(RuntimeError,
                       match=f"Environment variable {VARIABLE} is not set"):
        settings.get_env(VARIABLE)


def test_database_url_reads_database_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite://")

    assert settings.database_url() == "sqlite://"
