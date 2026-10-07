from fastapi.testclient import TestClient


def test_period_without_transactions(client: TestClient):
    assert client.get("/api/period").json() == \
        {"first_month": None, "last_month": None, "default_month": None}


def test_period(client: TestClient, add):
    add("2026-01-31", "MARKET", -10)
    add("2026-03-02", "MARKET", -10)

    assert client.get("/api/period").json() == {
        "first_month": "2026-01",
        "last_month": "2026-03",
        "default_month": "2026-02",
    }


def test_overview_defaults_to_the_last_complete_month(client: TestClient,
                                                      add):
    add("2026-02-10", "SALARY", 100)
    add("2026-03-02", "MARKET", -10)

    body = client.get("/api/overview").json()

    assert body["month"] == "2026-02"
    assert body["income"]["value"] == 100
    assert len(body["flow"]) == 12


def test_overview_of_a_month(client: TestClient, add):
    add("2026-02-10", "SALARY", 100)

    assert client.get("/api/overview?month=2026-01").json()["month"] == \
        "2026-01"


def test_overview_without_transactions(client: TestClient):
    response = client.get("/api/overview")

    assert response.status_code == 404
    assert response.json() == {"detail": "No transactions"}


def test_overview_rejects_invalid_months(client: TestClient):
    assert client.get("/api/overview?month=2026-13").status_code == 422


def test_web_pages_are_served(client: TestClient):
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
