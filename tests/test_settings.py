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


def test_dashboard_address_defaults_to_localhost(monkeypatch):
    monkeypatch.delenv("DASHBOARD_HOST", raising=False)
    monkeypatch.delenv("DASHBOARD_PORT", raising=False)

    assert (settings.dashboard_host(), settings.dashboard_port()) == \
        ("127.0.0.1", 8000)


def test_dashboard_address_reads_the_environment(monkeypatch):
    monkeypatch.setenv("DASHBOARD_HOST", "0.0.0.0")
    monkeypatch.setenv("DASHBOARD_PORT", "9000")

    assert (settings.dashboard_host(), settings.dashboard_port()) == \
        ("0.0.0.0", 9000)
