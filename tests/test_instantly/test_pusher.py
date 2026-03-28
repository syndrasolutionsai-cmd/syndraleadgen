import pytest
from unittest.mock import AsyncMock, patch
from leadforge.instantly.pusher import InstantlyPusher, PushResult


MOCK_LEADS = [
    {
        "email": "john@acme.com",
        "firstName": "John",
        "lastName": "Smith",
        "companyName": "Acme Corp",
        "email_subject": "Scaling outbound past 1M ARR",
        "email_body": "Your post about 1M ARR...",
    }
]


@pytest.mark.asyncio
async def test_pusher_uploads_leads():
    pusher = InstantlyPusher(api_key="test-key")

    with patch.object(pusher.client, "add_leads_to_campaign", new_callable=AsyncMock, return_value={"status": "success"}):
        result = await pusher.push(
            campaign_id="camp-instantly-123",
            leads=MOCK_LEADS,
        )
    assert isinstance(result, PushResult)
    assert result.success_count == 1
    assert result.failed_count == 0


@pytest.mark.asyncio
async def test_pusher_batches_100_at_a_time():
    pusher = InstantlyPusher(api_key="test-key")
    leads = [{"email": f"user{i}@co.com", "firstName": "U", "lastName": str(i), "companyName": "Co"} for i in range(250)]
    call_count = 0

    async def mock_add(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return {"status": "success"}

    with patch.object(pusher.client, "add_leads_to_campaign", side_effect=mock_add):
        result = await pusher.push("camp-123", leads)

    assert call_count == 3  # 100 + 100 + 50 = 3 calls
    assert result.success_count == 250
