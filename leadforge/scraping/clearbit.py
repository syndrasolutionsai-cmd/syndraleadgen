import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from leadforge.scraping.base import BaseScraper, ProspectRaw, ScraperSource, Signal


class ClearbitScraper(BaseScraper):
    """Enriches a known email/domain with Clearbit's combined lookup."""

    BASE_URL = "https://person-stream.clearbit.com/v2/combined/find"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def search(self, icp_config: dict, campaign_id: str, limit: int) -> list[ProspectRaw]:
        # Clearbit is an enrichment API — called per-prospect by Aggregator
        return []

    async def enrich(self, email: str) -> ProspectRaw | None:
        """Enrich a known email address with person + company data."""
        data = await self._combined_lookup(email)
        if not data:
            return None
        person = data.get("person", {}) or {}
        company = data.get("company", {}) or {}

        name = person.get("name", {}) or {}
        first = name.get("givenName", "")
        last = name.get("familyName", "")
        if not first or not last:
            return None

        employment = person.get("employment", {}) or {}
        geo = person.get("geo", {}) or {}
        metrics = company.get("metrics", {}) or {}

        tech_stack = company.get("tech", []) or []

        signals = []
        # Tech stack as a signal
        if tech_stack:
            signals.append(Signal(
                signal_type="tech_stack",
                text=f"Uses: {', '.join(tech_stack[:5])}",
                source=ScraperSource.CLEARBIT,
                confidence=0.9,
                metadata={"tech": tech_stack},
            ))

        return ProspectRaw(
            first_name=first,
            last_name=last,
            role=employment.get("title"),
            email=email,
            company_name=employment.get("name") or company.get("name", ""),
            company_size=metrics.get("employees"),
            industry=", ".join(company.get("tags", [])[:3]),
            geography=geo.get("country"),
            tech_stack=tech_stack,
            source=ScraperSource.CLEARBIT,
            signals=signals,
            enriched_data={
                "clearbit_person": person,
                "clearbit_company": company,
                "estimated_revenue": metrics.get("estimatedAnnualRevenue"),
            },
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    async def _combined_lookup(self, email: str) -> dict | None:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                self.BASE_URL,
                params={"email": email},
                auth=(self.api_key, ""),
            )
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json()
