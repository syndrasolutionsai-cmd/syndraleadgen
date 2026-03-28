import asyncio
from dataclasses import dataclass, field
from leadforge.instantly.client import InstantlyClient

BATCH_SIZE = 100


@dataclass
class PushResult:
    campaign_id: str
    success_count: int = 0
    failed_count: int = 0
    errors: list[str] = field(default_factory=list)


class InstantlyPusher:
    def __init__(self, api_key: str):
        self.client = InstantlyClient(api_key)

    async def push(self, campaign_id: str, leads: list[dict]) -> PushResult:
        """
        Upload leads to an Instantly campaign in batches of 100.
        Each lead dict must have: email, firstName, lastName, companyName.
        """
        result = PushResult(campaign_id=campaign_id)
        batches = [leads[i:i + BATCH_SIZE] for i in range(0, len(leads), BATCH_SIZE)]

        for batch in batches:
            try:
                await self.client.add_leads_to_campaign(campaign_id, batch)
                result.success_count += len(batch)
            except Exception as e:
                result.failed_count += len(batch)
                result.errors.append(str(e))
            await asyncio.sleep(0.5)

        return result

    async def get_or_create_campaign(self, client_id: str, batch_id: str) -> str:
        """Get existing Instantly campaign or create new one. Returns campaign_id."""
        name = f"LeadForge | {client_id} | {batch_id}"
        response = await self.client.create_campaign(name)
        return response.get("id") or response.get("campaign_id", "")
