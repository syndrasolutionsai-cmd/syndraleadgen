import pytest
from unittest.mock import AsyncMock, patch
from leadforge.scraping.clearbit import ClearbitScraper
from leadforge.scraping.base import ScraperSource

MOCK_CLEARBIT_RESPONSE = {
    "person": {
        "name": {"givenName": "Alice", "familyName": "Wong"},
        "employment": {"title": "VP Sales", "name": "TechCorp"},
        "linkedin": {"handle": "alicewong"},
        "geo": {"country": "US"},
    },
    "company": {
        "name": "TechCorp",
        "metrics": {"employees": 120, "estimatedAnnualRevenue": "10M-50M"},
        "tech": ["HubSpot", "Salesforce", "Intercom"],
        "tags": ["SaaS", "B2B"],
    },
}


@pytest.mark.asyncio
async def test_clearbit_extracts_tech_stack():
    scraper = ClearbitScraper(api_key="test-key")
    with patch.object(scraper, "_combined_lookup", new_callable=AsyncMock, return_value=MOCK_CLEARBIT_RESPONSE):
        result = await scraper.enrich("alice@techcorp.com")
    assert result is not None
    assert "HubSpot" in result.tech_stack
    assert result.source == ScraperSource.CLEARBIT
