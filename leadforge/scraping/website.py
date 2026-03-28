import re
import httpx
from bs4 import BeautifulSoup
from leadforge.scraping.base import BaseScraper, ProspectRaw, ScraperSource, Signal

# Tech stack detection patterns: {tool_name: [url_patterns]}
TECH_PATTERNS = {
    "HubSpot": ["hsforms.net", "hs-scripts.com", "hubspot.com"],
    "Salesforce": ["salesforce.com", "force.com", "pardot.com"],
    "Intercom": ["intercom.io", "widget.intercom.io"],
    "Segment": ["segment.com", "cdn.segment.com"],
    "Drift": ["drift.com", "js.driftt.com"],
    "Marketo": ["marketo.com", "mktoweb.com"],
    "Zendesk": ["zendesk.com", "zdassets.com"],
    "Mixpanel": ["mixpanel.com", "cdn.mxpnl.com"],
    "Heap": ["heapanalytics.com", "cdn.heapanalytics.com"],
    "Amplitude": ["amplitude.com", "cdn.amplitude.com"],
}

SDR_JOB_KEYWORDS = [
    "sales development representative", "sdr", "business development representative",
    "bdr", "outbound sales", "cold calling", "prospecting", "account executive", "ae"
]


class WebsiteScraper(BaseScraper):
    async def search(self, icp_config: dict, campaign_id: str, limit: int) -> list[ProspectRaw]:
        # Website scraper enriches existing prospects, not discover new ones
        return []

    async def extract_signals(self, url: str) -> list[Signal]:
        """Extract tech stack and job posting signals from a company website."""
        signals = []
        try:
            html = await self._fetch_html(url)
            signals.extend(self._detect_tech_stack(html))
            signals.extend(self._detect_job_postings(html))
        except Exception:
            pass  # Website unreachable — return empty signals
        return signals

    async def _fetch_html(self, url: str) -> str:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            return resp.text

    def _detect_tech_stack(self, html: str) -> list[Signal]:
        signals = []
        for tool, patterns in TECH_PATTERNS.items():
            if any(p in html.lower() for p in patterns):
                signals.append(Signal(
                    signal_type="tech_stack",
                    text=f"Uses {tool} (detected on website)",
                    source=ScraperSource.WEBSITE,
                    confidence=0.85,
                    metadata={"tool": tool},
                ))
        return signals

    def _detect_job_postings(self, html: str) -> list[Signal]:
        signals = []
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ").lower()
        for keyword in SDR_JOB_KEYWORDS:
            if keyword in text:
                signals.append(Signal(
                    signal_type="job_posting",
                    text=f"Hiring for: {keyword.title()} (found on careers page)",
                    source=ScraperSource.WEBSITE,
                    confidence=0.80,
                    metadata={"keyword": keyword},
                ))
                break  # one job signal is enough
        return signals
