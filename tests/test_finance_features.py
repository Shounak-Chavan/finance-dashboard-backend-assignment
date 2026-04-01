from fastapi.testclient import TestClient


def bootstrap_admin_and_login(client: TestClient) -> str:
    # Create initial admin through bootstrap endpoint.
    bootstrap_res = client.post("/users/bootstrap-admin", json={
        "name": "Admin",
        "email": "admin@example.com",
        "password": "StrongPass123",
        "role": "viewer"
    })
    assert bootstrap_res.status_code == 200

    # 🔥 Login
    res = client.post(
        "/auth/login",
        data={
            "username": "admin@example.com",
            "password": "StrongPass123"
        },
    )

    assert res.status_code == 200
    return res.json()["access_token"]


def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


def test_create_record(client: TestClient):
    token = bootstrap_admin_and_login(client)
    headers = auth_headers(token)

    res = client.post(
        "/records/",
        headers=headers,
        json={
            "amount": 1000,
            "type": "income",
            "category": "salary",
            "date": "2026-04-01",
            "note": "April salary"
        },
    )

    assert res.status_code == 200
    assert res.json()["amount"] == 1000


def test_delete_record(client: TestClient):
    token = bootstrap_admin_and_login(client)
    headers = auth_headers(token)

    create = client.post(
        "/records/",
        headers=headers,
        json={
            "amount": 500,
            "type": "expense",
            "category": "food",
            "date": "2026-04-01"
        },
    )

    record_id = create.json()["id"]

    delete = client.delete(f"/records/{record_id}", headers=headers)

    assert delete.status_code == 200


def test_summary(client: TestClient):
    token = bootstrap_admin_and_login(client)
    headers = auth_headers(token)

    client.post(
        "/records/",
        headers=headers,
        json={
            "amount": 2000,
            "type": "income",
            "category": "salary",
            "date": "2026-04-01"
        },
    )

    res = client.get("/summary/", headers=headers)

    assert res.status_code == 200
    assert res.json()["total_income"] == 2000