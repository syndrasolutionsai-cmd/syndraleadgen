import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


class InstantlyClient:
    """Thin wrapper around the Instantly.ai REST API v1."""

    BASE_URL = "https://api.instantly.ai/api/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def create_campaign(self, name: str) -> dict:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.BASE_URL}/campaign/create",
                json={"name": name, "api_key": self.api_key},
            )
            resp.raise_for_status()
            return resp.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def add_leads_to_campaign(self, campaign_id: str, leads: list[dict]) -> dict:
        """Add a batch of leads (max 100) to a campaign."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.BASE_URL}/lead/add",
                json={
                    "api_key": self.api_key,
                    "campaign_id": campaign_id,
                    "skip_if_in_workspace": True,
                    "leads": leads,
                },
            )
            resp.raise_for_status()
            return resp.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def get_campaign_analytics(self, campaign_id: str) -> dict:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{self.BASE_URL}/analytics/campaign/summary",
                params={"api_key": self.api_key, "id": campaign_id},
            )
            resp.raise_for_status()
            return resp.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def get_lead_status(self, campaign_id: str, email: str) -> dict:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{self.BASE_URL}/lead/get",
                params={"api_key": self.api_key, "campaign_id": campaign_id, "email": email},
            )
            resp.raise_for_status()
            return resp.json()
