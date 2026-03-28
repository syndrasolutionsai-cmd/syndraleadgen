# tests/test_review/test_review_api.py
import pytest
import uuid


async def _auth_header(client, email="reviewer@test.com", password="pass123"):
    await client.post("/clients/", json={"name": "R", "email": email, "password": password})
    resp = await client.post("/auth/token", data={"username": email, "password": password})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.mark.asyncio
async def test_get_review_queue_empty(client):
    headers = await _auth_header(client, "rv2@test.com", "pw")
    # Create campaign first
    camp_resp = await client.post("/campaigns/", json={"name": "Test", "icp_config": {}}, headers=headers)
    camp_id = camp_resp.json()["id"]
    resp = await client.get(f"/review/{camp_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_approve_email(client):
    headers = await _auth_header(client, "rv3@test.com", "pw")
    # This test requires a seeded email in the DB — seed it via direct DB insert in conftest
    # Verify the endpoint returns 404 for non-existent email ID
    fake_id = str(uuid.uuid4())
    resp = await client.post(f"/review/approve/{fake_id}", headers=headers)
    assert resp.status_code == 404
