import pytest


@pytest.mark.asyncio
async def test_login_returns_token(client):
    await client.post("/clients/", json={
        "name": "Test Agency",
        "email": "test@agency.com",
        "password": "secret123"
    })
    resp = await client.post("/auth/token", data={
        "username": "test@agency.com",
        "password": "secret123"
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    resp = await client.post("/auth/token", data={
        "username": "test@agency.com",
        "password": "wrong"
    })
    assert resp.status_code == 401
