import pytest


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_transaction(client, sample_transaction):
    response = client.post("/api/v1/transactions/", json=sample_transaction)
    assert response.status_code == 200
    data = response.json()
    assert data["transaction_id"] == "txn_test_001"
    assert data["amount"] == 150.00


def test_get_transaction(client, sample_transaction):
    client.post("/api/v1/transactions/", json=sample_transaction)
    response = client.get("/api/v1/transactions/txn_test_001")
    assert response.status_code == 200
    assert response.json()["user_id"] == "user_42"


def test_get_transaction_not_found(client):
    response = client.get("/api/v1/transactions/nonexistent_txn")
    assert response.status_code == 404


def test_list_transactions_returns_200(client):
    response = client.get("/api/v1/transactions/")
    assert response.status_code == 200
    data = response.json()
    assert "transactions" in data
    assert "total" in data


def test_create_duplicate_returns_409(client, sample_transaction):
    client.post("/api/v1/transactions/", json=sample_transaction)
    response = client.post("/api/v1/transactions/", json=sample_transaction)
    assert response.status_code == 409


def test_transaction_fields_persisted(client, sample_transaction):
    client.post("/api/v1/transactions/", json=sample_transaction)
    response = client.get("/api/v1/transactions/txn_test_001")
    data = response.json()
    assert data["merchant_category"] == "grocery"
    assert data["status"] == "pending"


def test_list_transactions_pagination(client):
    for i in range(3):
        txn = {
            "transaction_id": f"txn_page_{i}",
            "user_id": "user_page",
            "amount": 10.0 * (i + 1),
            "merchant_id": "m1",
            "merchant_category": "retail",
            "location_lat": 40.0,
            "location_lon": -74.0,
            "timestamp": f"2024-06-15T10:0{i}:00",
        }
        client.post("/api/v1/transactions/", json=txn)
    response = client.get("/api/v1/transactions/?page=1&page_size=2")
    data = response.json()
    assert len(data["transactions"]) == 2
    assert data["total"] == 3
