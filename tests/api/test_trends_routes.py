from fastapi.testclient import TestClient


def test_recurring(client: TestClient, add):
    for month in range(1, 13):
        add(f"2026-{month:02d}-05", "RENT", -1000, "Home")

    body = client.get("/api/recurring?month=2026-12").json()

    assert body["monthly_cost"] == 1000
    assert body["items"][0]["merchant"] == "RENT"


def test_category_variance(client: TestClient, add):
    add("2026-01-05", "MARKET", -100, "Market")
    add("2026-02-05", "MARKET", -300, "Market")

    body = client.get("/api/category-variance?month=2026-02").json()

    assert body == [{"category": "Market", "sector": "Essential",
                     "value": 300, "average": 100, "difference": 200,
                     "ratio": 2.0}]


def test_seasonality(client: TestClient, add):
    add("2026-01-05", "MARKET", -100)

    assert client.get("/api/seasonality").json() == \
        [{"month": 1, "average": 100, "samples": 1}]


def test_largest_expenses(client: TestClient, add):
    add("2026-01-05", "SMALL", -1)
    add("2026-01-06", "BIG", -100)

    body = client.get("/api/largest-expenses?start=2026-01&end=2026-01"
                      "&limit=1").json()

    assert [expense["description"] for expense in body] == ["BIG"]
