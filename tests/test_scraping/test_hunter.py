import pytest
from unittest.mock import AsyncMock, patch
from leadforge.scraping.hunter import HunterScraper
from leadforge.scraping.base import ScraperSource

MOCK_HUNTER_RESPONSE = {
    "data": {
        "emails": [
            {
                "value": "john@acme.com",
                "first_name": "John",
                "last_name": "Smith",
                "position": "CEO",
                "confidence": 92,
                "linkedin": "https://linkedin.com/in/johnsmith",
            }
        ],
        "organization": {"name": "Acme Corp", "size": 50},
    }
}


@pytest.mark.asyncio
async def test_hunter_returns_prospect_with_email():
    scraper = HunterScraper(api_key="test-key")
    with patch.object(scraper, "_domain_search", new_callable=AsyncMock, return_value=MOCK_HUNTER_RESPONSE):
        results = await scraper.find_emails_for_domain("acme.com", ["CEO"])
    assert len(results) == 1
    assert results[0].email == "john@acme.com"
    assert results[0].source == ScraperSource.HUNTER
