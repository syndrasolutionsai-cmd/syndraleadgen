import pytest


async def _auth_header(client, email="camp@example.com", password="pass123"):
    await client.post("/clients/", json={"name": "C", "email": email, "password": password})
    resp = await client.post("/auth/token", data={"username": email, "password": password})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_campaign(client):
    headers = await _auth_header(client)
    resp = await client.post("/campaigns/", json={
        "name": "SaaS Q2",
        "niche": "B2B SaaS",
        "batch_size": 500,
        "icp_config": {"industries": ["SaaS"], "roles": ["CEO"], "min_icp_score": 70}
    }, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["name"] == "SaaS Q2"


@pytest.mark.asyncio
async def test_list_campaigns_only_own(client):
    headers = await _auth_header(client, "own@example.com", "pass")
    await client.post("/campaigns/", json={"name": "Mine", "icp_config": {}}, headers=headers)
    resp = await client.get("/campaigns/", headers=headers)
    assert resp.status_code == 200
    assert all(c["name"] == "Mine" for c in resp.json())


@pytest.mark.asyncio
async def test_unauthenticated_rejected(client):
    resp = await client.get("/campaigns/")
    assert resp.status_code == 401
