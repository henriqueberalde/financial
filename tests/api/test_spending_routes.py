from fastapi.testclient import TestClient


def add_expenses(add):
    add("2025-12-10", "OLD", -999, "Market")
    add("2026-01-10", "MARKET A", -100, "Market")
    add("2026-02-10", "MARKET B", -50, "Market", balance=None)
    add("2026-02-11", "BAR", -30, "Bar", "Leisure")


def test_tree(client: TestClient, add):
    add_expenses(add)

    body = client.get("/api/spending/tree?start=2026-01&end=2026-02").json()

    assert [(node["name"], node["value"]) for node in body] == \
        [("Essential", 150), ("Leisure", 30)]


def test_tree_defaults_to_the_trailing_months(client: TestClient, add):
    add_expenses(add)
    add("2026-03-31", "BAR", -1, "Bar", "Leisure")

    body = client.get("/api/spending/tree").json()

    assert [(node["name"], node["value"]) for node in body] == \
        [("Essential", 1149), ("Leisure", 31)]


def test_period_must_be_ordered(client: TestClient, add):
    add_expenses(add)

    response = client.get("/api/spending/tree?start=2026-03&end=2026-01")

    assert response.status_code == 422


def test_timeline_of_a_drill(client: TestClient, add):
    add_expenses(add)

    body = client.get("/api/spending/timeline?start=2026-01&end=2026-02"
                      "&sector=Essential&category=Market&source=card").json()

    assert body["granularity"] == "month"
    assert body["points"] == [{"period": "2026-01", "value": 0},
                              {"period": "2026-02", "value": 50}]


def test_timeline_by_year(client: TestClient, add):
    add_expenses(add)

    body = client.get("/api/spending/timeline?start=2025-12&end=2026-02"
                      "&granularity=year").json()

    assert [point["period"] for point in body["points"]] == ["2025", "2026"]


def test_merchants(client: TestClient, add):
    add_expenses(add)

    body = client.get("/api/spending/merchants?start=2026-01&end=2026-02"
                      "&limit=1").json()

    assert body == [{"name": "MARKET A", "count": 1, "total": 100}]


def test_transactions(client: TestClient, add):
    add_expenses(add)

    body = client.get("/api/transactions?start=2026-01&end=2026-02"
                      "&search=market&merchant=MARKET A").json()

    assert (body["total"], body["amount"]) == (1, 100)
    assert body["items"][0]["date"] == "2026-01-10"
    assert body["items"][0]["source"] == "account"
