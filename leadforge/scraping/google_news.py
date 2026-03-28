import httpx
from leadforge.scraping.base import BaseScraper, ProspectRaw, ScraperSource, Signal


class GoogleNewsScraper(BaseScraper):
    """Finds recent funding/milestone news via SerpAPI."""

    BASE_URL = "https://serpapi.com/search"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def search(self, icp_config: dict, campaign_id: str, limit: int) -> list[ProspectRaw]:
        return []  # News scraper enriches — doesn't discover new prospects

    async def find_news_signals(self, company_name: str) -> list[Signal]:
        """Search for recent news about a company."""
        signals = []
        try:
            results = await self._search(f'"{company_name}" funding OR launch OR expansion OR award site:techcrunch.com OR site:businesswire.com OR site:prnewswire.com')
            for item in results[:3]:
                title = item.get("title", "")
                snippet = item.get("snippet", "")
                date = item.get("date", "")
                if any(kw in (title + snippet).lower() for kw in ["raised", "funding", "launched", "expanded", "award", "named"]):
                    signals.append(Signal(
                        signal_type="funding",
                        text=f"{title} — {snippet[:200]}",
                        source=ScraperSource.GOOGLE_NEWS,
                        confidence=0.88,
                        metadata={"url": item.get("link"), "date": date},
                    ))
        except Exception:
            pass
        return signals

    async def _search(self, query: str) -> list[dict]:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(
                self.BASE_URL,
                params={"q": query, "api_key": self.api_key, "engine": "google", "num": 5, "tbm": "nws"},
            )
            resp.raise_for_status()
            return resp.json().get("news_results", [])
