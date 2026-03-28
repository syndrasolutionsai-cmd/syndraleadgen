import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from leadforge.scraping.base import BaseScraper, ProspectRaw, ScraperSource


class HunterScraper(BaseScraper):
    """Finds corporate emails by company domain using Hunter.io domain-search."""

    BASE_URL = "https://api.hunter.io/v2"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def search(self, icp_config: dict, campaign_id: str, limit: int) -> list[ProspectRaw]:
        """
        Hunter doesn't do prospect search — it enriches known domains.
        In the pipeline, it's called by the Aggregator with a list of domains
        found from other sources. For standalone use it searches a known company list.
        """
        # In practice this is called per-domain by the Aggregator
        return []

    async def find_emails_for_domain(self, domain: str, roles: list[str]) -> list[ProspectRaw]:
        """Find email addresses for a specific company domain."""
        data = await self._domain_search(domain)
        emails = data.get("data", {}).get("emails", [])
        org = data.get("data", {}).get("organization", {})

        results = []
        for item in emails:
            position = item.get("position", "")
            if roles and not any(r.lower() in position.lower() for r in roles):
                continue
            results.append(ProspectRaw(
                first_name=item.get("first_name", "").strip(),
                last_name=item.get("last_name", "").strip(),
                role=position,
                email=item.get("value"),
                company_name=org.get("name", domain),
                company_size=org.get("size"),
                linkedin_url=item.get("linkedin"),
                source=ScraperSource.HUNTER,
                enriched_data={"hunter_confidence": item.get("confidence", 0)},
            ))
        return results

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    async def _domain_search(self, domain: str) -> dict:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{self.BASE_URL}/domain-search",
                params={"domain": domain, "api_key": self.api_key, "limit": 20},
            )
            resp.raise_for_status()
            return resp.json()
