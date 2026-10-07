import pytest

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from financial.api.app import create_app
from financial.api.dependencies import get_session


@pytest.fixture()
def client(session: Session) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_session] = lambda: session

    return TestClient(app)
