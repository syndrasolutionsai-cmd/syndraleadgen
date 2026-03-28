import httpx
from bs4 import BeautifulSoup
from leadforge.scraping.base import BaseScraper, ProspectRaw, ScraperSource, Signal

PAIN_KEYWORDS = [
    "difficult to", "hard to", "struggle", "lacking", "missing", "wish it had",
    "no integration", "expensive", "slow", "poor support", "confusing", "limited"
]


class ReviewSitesScraper(BaseScraper):
    async def search(self, icp_config: dict, campaign_id: str, limit: int) -> list[ProspectRaw]:
        return []  # Enrichment only

    async def find_pain_signals(self, company_name: str) -> list[Signal]:
        """Scrape G2 reviews for recurring pain points about a company's product/space."""
        signals = []
        try:
            # Search G2 for the company
            slug = company_name.lower().replace(" ", "-")
            url = f"https://www.g2.com/products/{slug}/reviews"
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
                if resp.status_code != 200:
                    return []
            soup = BeautifulSoup(resp.text, "html.parser")
            review_texts = [r.get_text()[:300] for r in soup.select(".review-text, .paper p")[:10]]
            for text in review_texts:
                if any(kw in text.lower() for kw in PAIN_KEYWORDS):
                    signals.append(Signal(
                        signal_type="review_pain",
                        text=text[:200],
                        source=ScraperSource.REVIEW_SITES,
                        confidence=0.75,
                        metadata={"source": "g2"},
                    ))
                    break  # one pain signal per company is enough
        except Exception:
            pass
        return signals
