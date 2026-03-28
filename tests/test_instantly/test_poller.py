# tests/test_instantly/test_poller.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from leadforge.instantly.poller import MetricsPoller


MOCK_ANALYTICS = {
    "open_count": 45,
    "reply_count": 12,
    "click_count": 8,
    "leads_count": 300,
}


@pytest.mark.asyncio
async def test_poller_returns_metrics():
    mock_db = AsyncMock()
    poller = MetricsPoller(instantly_api_key="test-key", db=mock_db)

    with patch.object(poller.client, "get_campaign_analytics", new_callable=AsyncMock, return_value=MOCK_ANALYTICS):
        metrics = await poller.poll_campaign("camp-instantly-123", "camp-db-uuid")

    assert metrics["open_rate"] == pytest.approx(45 / 300, rel=1e-3)
    assert metrics["reply_rate"] == pytest.approx(12 / 300, rel=1e-3)
    assert metrics["open_count"] == 45
