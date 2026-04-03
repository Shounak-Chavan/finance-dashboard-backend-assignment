import pytest
from fastapi.testclient import TestClient


# login using seeded admin (from conftest)
def bootstrap_admin_and_login(client: TestClient) -> str:
    res = client.post(
        "/auth/login",
        data={
            "username": "admin@example.com",
            "password": "admin123",
        },
    )

    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# CREATE
def test_create_record(client: TestClient):
    headers = auth_headers(bootstrap_admin_and_login(client))

    res = client.post(
        "/records/",
        headers=headers,
        json={
            "amount": 1000,
            "type": "income",
            "category": "salary",
            "date": "2026-04-01",
            "note": "April salary",
        },
    )

    assert res.status_code == 201, res.text
    data = res.json()

    assert data["amount"] == 1000
    assert data["type"] == "income"


# DELETE (SOFT DELETE)
def test_delete_record(client: TestClient):
    headers = auth_headers(bootstrap_admin_and_login(client))

    create = client.post(
        "/records/",
        headers=headers,
        json={
            "amount": 500,
            "type": "expense",
            "category": "food",
            "date": "2026-04-01",
        },
    )

    assert create.status_code == 201
    record_id = create.json()["id"]

    delete = client.delete(f"/records/{record_id}", headers=headers)
    assert delete.status_code == 200

    # ensure listing still works
    get = client.get("/records/", headers=headers)
    assert get.status_code == 200


# SUMMARY
def test_summary(client: TestClient):
    headers = auth_headers(bootstrap_admin_and_login(client))

    client.post(
        "/records/",
        headers=headers,
        json={
            "amount": 2000,
            "type": "income",
            "category": "salary",
            "date": "2026-04-01",
        },
    )

    res = client.get("/summary/", headers=headers)

    assert res.status_code == 200
    data = res.json()

    assert data["total_income"] == 2000


# INCOME + EXPENSE
def test_summary_with_expense(client: TestClient):
    headers = auth_headers(bootstrap_admin_and_login(client))

    client.post("/records/", headers=headers, json={
        "amount": 3000,
        "type": "income",
        "category": "salary",
        "date": "2026-04-01"
    })

    client.post("/records/", headers=headers, json={
        "amount": 500,
        "type": "expense",
        "category": "food",
        "date": "2026-04-02"
    })

    res = client.get("/summary/", headers=headers)

    assert res.status_code == 200
    data = res.json()

    assert data["total_income"] == 3000
    assert data["total_expense"] == 500
    assert data["net_balance"] == 2500