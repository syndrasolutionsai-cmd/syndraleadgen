# leadforge/instantly/poller.py
from sqlalchemy.ext.asyncio import AsyncSession
from leadforge.instantly.client import InstantlyClient


class MetricsPoller:
    def __init__(self, instantly_api_key: str, db: AsyncSession):
        self.client = InstantlyClient(instantly_api_key)
        self.db = db

    async def poll_campaign(self, instantly_campaign_id: str, db_campaign_id: str) -> dict:
        """
        Poll Instantly for campaign metrics and return computed rates.
        Persisting to DB is handled by the calling Prefect flow.
        """
        raw = await self.client.get_campaign_analytics(instantly_campaign_id)

        leads_count = raw.get("leads_count") or 1  # avoid division by zero
        open_count = raw.get("open_count", 0)
        reply_count = raw.get("reply_count", 0)
        click_count = raw.get("click_count", 0)

        return {
            "instantly_campaign_id": instantly_campaign_id,
            "db_campaign_id": db_campaign_id,
            "leads_count": leads_count,
            "open_count": open_count,
            "reply_count": reply_count,
            "click_count": click_count,
            "open_rate": round(open_count / leads_count, 4),
            "reply_rate": round(reply_count / leads_count, 4),
            "click_rate": round(click_count / leads_count, 4),
        }
