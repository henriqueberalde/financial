from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from financial.models.category import Category
from financial.models.category_rule import CategoryRule
from financial.models.transaction import Transaction


def add_category(session: Session, name: str = "Gas") -> Category:
    category = Category(name=name, sector="Essential")
    session.add(category)
    session.commit()
    return category


def test_categories(client: TestClient, session: Session):
    add_category(session, "Water")
    add_category(session, "Gas")

    assert [c["name"] for c in client.get("/api/categories").json()] == \
        ["Gas", "Water"]


def test_update_transaction_category(client: TestClient, session: Session,
                                     add):
    category = add_category(session)
    transaction = add("2026-01-05", "POSTO", -100)

    response = client.put(f"/api/transactions/{transaction.id}/category",
                          json={"category_id": category.id})

    assert response.status_code == 204
    assert session.get(Transaction, transaction.id).category_id == \
        category.id


def test_update_category_of_missing_transaction(client: TestClient,
                                                session: Session):
    category = add_category(session)

    response = client.put("/api/transactions/999/category",
                          json={"category_id": category.id})

    assert response.status_code == 404
    assert response.json() == {"detail": "Transaction 999 not found"}


def test_update_transaction_to_missing_category(client: TestClient, add):
    transaction = add("2026-01-05", "POSTO", -100)

    response = client.put(f"/api/transactions/{transaction.id}/category",
                          json={"category_id": 999})

    assert response.status_code == 404


def test_create_category_rule(client: TestClient, session: Session, add):
    category = add_category(session)
    transaction = add("2026-01-05", "AUTO POSTO", -100)

    response = client.post("/api/category-rules",
                           json={"category_id": category.id,
                                 "rule": "posto"})

    assert response.status_code == 201
    assert response.json() == {"conflicts": []}
    assert session.get(Transaction, transaction.id).category_id == \
        category.id


def test_create_invalid_category_rule(client: TestClient, session: Session):
    category = add_category(session)

    response = client.post("/api/category-rules",
                           json={"category_id": category.id,
                                 "rule": "posto("})

    assert response.status_code == 422
    assert session.query(CategoryRule).count() == 0


def test_categorization_quality(client: TestClient, add):
    add("2026-01-05", "UNKNOWN", -100)

    body = client.get("/api/categorization-quality?month=2026-01").json()

    assert body["share"] == 1
    assert body["merchants"][0]["merchant"] == "UNKNOWN"
