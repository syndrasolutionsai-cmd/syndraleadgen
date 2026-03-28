import pytest
from unittest.mock import AsyncMock, patch
from leadforge.scraping.linkedin import LinkedInScraper
from leadforge.scraping.base import ScraperSource


MOCK_APIFY_RESULT = [
    {
        "firstName": "Sarah",
        "lastName": "Chen",
        "title": "CEO",
        "companyName": "GrowthCo",
        "profileUrl": "https://linkedin.com/in/sarahchen",
        "location": "San Francisco, CA",
        "companySize": "51-200",
        "recentPosts": [
            {"text": "We just hit 1M ARR — wild ride!", "date": "2026-03-20"}
        ],
    }
]


@pytest.mark.asyncio
async def test_linkedin_scraper_returns_prospects():
    scraper = LinkedInScraper(api_token="test-token")
    with patch.object(scraper, "_run_apify_actor", new_callable=AsyncMock, return_value=MOCK_APIFY_RESULT):
        results = await scraper.search(
            icp_config={"roles": ["CEO"], "industries": ["SaaS"], "geography": ["US"]},
            campaign_id="camp-1",
            limit=10,
        )
    assert len(results) == 1
    assert results[0].first_name == "Sarah"
    assert results[0].source == ScraperSource.LINKEDIN
    assert len(results[0].signals) == 1
    assert results[0].signals[0].signal_type == "linkedin_activity"


@pytest.mark.asyncio
async def test_linkedin_no_results_returns_empty():
    scraper = LinkedInScraper(api_token="test-token")
    with patch.object(scraper, "_run_apify_actor", new_callable=AsyncMock, return_value=[]):
        results = await scraper.search({}, "camp-1", 10)
    assert results == []
