import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from leadforge.scraping.base import BaseScraper, ProspectRaw, ScraperSource, Signal

# Apify Actor for LinkedIn People Search
LINKEDIN_ACTOR_ID = "curious_coder/linkedin-people-search-scraper"


class LinkedInScraper(BaseScraper):
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.apify.com/v2"

    async def search(self, icp_config: dict, campaign_id: str, limit: int) -> list[ProspectRaw]:
        raw_items = await self._run_apify_actor(icp_config, limit)
        return [self._parse(item) for item in raw_items if self._is_valid(item)]

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _run_apify_actor(self, icp_config: dict, limit: int) -> list[dict]:
        """Run the Apify LinkedIn actor and wait for results."""
        roles = icp_config.get("roles", [])
        industries = icp_config.get("industries", [])
        geography = icp_config.get("geography", [])

        input_data = {
            "searchQueries": [f"{role} {ind}" for role in roles[:2] for ind in industries[:2]],
            "maxResults": limit,
            "locations": geography,
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            # Start the actor run
            run_resp = await client.post(
                f"{self.base_url}/acts/{LINKEDIN_ACTOR_ID}/runs",
                params={"token": self.api_token},
                json={"runInput": input_data},
            )
            run_resp.raise_for_status()
            run_id = run_resp.json()["data"]["id"]

            # Poll until finished
            import asyncio
            for _ in range(60):  # max 10 minutes
                await asyncio.sleep(10)
                status_resp = await client.get(
                    f"{self.base_url}/actor-runs/{run_id}",
                    params={"token": self.api_token},
                )
                status = status_resp.json()["data"]["status"]
                if status == "SUCCEEDED":
                    break
                if status in ("FAILED", "ABORTED", "TIMED-OUT"):
                    raise RuntimeError(f"Apify actor failed with status: {status}")

            # Fetch dataset
            dataset_id = status_resp.json()["data"]["defaultDatasetId"]
            data_resp = await client.get(
                f"{self.base_url}/datasets/{dataset_id}/items",
                params={"token": self.api_token, "limit": limit},
            )
            data_resp.raise_for_status()
            return data_resp.json()

    def _parse(self, item: dict) -> ProspectRaw:
        signals = []
        for post in item.get("recentPosts", []):
            if post.get("text"):
                signals.append(Signal(
                    signal_type="linkedin_activity",
                    text=post["text"][:500],
                    source=ScraperSource.LINKEDIN,
                    confidence=0.95,
                    metadata={"date": post.get("date", "")},
                ))

        # Parse company size range to midpoint int
        size_str = item.get("companySize", "")
        company_size = self._parse_size(size_str)

        return ProspectRaw(
            first_name=item.get("firstName", "").strip(),
            last_name=item.get("lastName", "").strip(),
            role=item.get("title"),
            company_name=item.get("companyName", "").strip(),
            linkedin_url=item.get("profileUrl"),
            geography=item.get("location"),
            company_size=company_size,
            source=ScraperSource.LINKEDIN,
            signals=signals,
            enriched_data={"linkedin_raw": item},
        )

    def _is_valid(self, item: dict) -> bool:
        return bool(item.get("firstName") and item.get("lastName") and item.get("companyName"))

    def _parse_size(self, size_str: str) -> int | None:
        """Convert '51-200' → 125 (midpoint)."""
        if not size_str:
            return None
        try:
            if "-" in size_str:
                lo, hi = size_str.split("-")
                return (int(lo.strip()) + int(hi.replace("+", "").strip())) // 2
            return int(size_str.replace("+", ""))
        except (ValueError, AttributeError):
            return None
