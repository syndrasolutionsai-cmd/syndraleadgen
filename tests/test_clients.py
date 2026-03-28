import pytest


@pytest.mark.asyncio
async def test_create_client(client):
    resp = await client.post("/clients/", json={
        "name": "Acme Agency",
        "email": "acme@example.com",
        "password": "secure123",
        "instantly_api_key": "sk-instantly-test"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Acme Agency"
    assert "password" not in data
    assert "instantly_api_key" not in data


@pytest.mark.asyncio
async def test_create_duplicate_email_fails(client):
    payload = {"name": "X", "email": "dup@example.com", "password": "abc"}
    await client.post("/clients/", json=payload)
    resp = await client.post("/clients/", json=payload)
    assert resp.status_code == 400
