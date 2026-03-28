from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ScraperSource(str, Enum):
    LINKEDIN = "linkedin"
    CRUNCHBASE = "crunchbase"
    HUNTER = "hunter"
    CLEARBIT = "clearbit"
    WEBSITE = "website"
    GOOGLE_NEWS = "google_news"
    REVIEW_SITES = "review_sites"


@dataclass
class Signal:
    """A personalization signal found during scraping/enrichment."""
    signal_type: str  # linkedin_activity | funding | job_posting | tech_stack | review_pain
    text: str
    source: ScraperSource
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProspectRaw:
    """Raw prospect data from a single scraping source."""
    first_name: str
    last_name: str
    company_name: str
    source: ScraperSource
    role: str | None = None
    email: str | None = None
    linkedin_url: str | None = None
    company_size: int | None = None
    industry: str | None = None
    geography: str | None = None
    tech_stack: list[str] = field(default_factory=list)
    signals: list[Signal] = field(default_factory=list)
    enriched_data: dict[str, Any] = field(default_factory=dict)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class BaseScraper(ABC):
    """All scrapers implement this interface."""

    @abstractmethod
    async def search(self, icp_config: dict, campaign_id: str, limit: int) -> list[ProspectRaw]:
        """
        Search for prospects matching the ICP.

        Args:
            icp_config: Parsed ICP dict (industries, roles, geography, etc.)
            campaign_id: For logging/tracking purposes
            limit: Max number of raw prospects to return

        Returns:
            List of ProspectRaw — may have overlapping data with other scrapers
        """
        ...
