import os

from dotenv import load_dotenv

load_dotenv()


def get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)

    if value is None:
        raise RuntimeError(
            f"Environment variable {name} is not set. "
            "Copy .env_example to .env and fill in its values."
        )

    return value


def database_url() -> str:
    return get_env("DATABASE_URL")
