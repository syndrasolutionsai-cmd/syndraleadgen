import pytest
from unittest.mock import AsyncMock, patch
from leadforge.scraping.website import WebsiteScraper


@pytest.mark.asyncio
async def test_extracts_job_postings():
    scraper = WebsiteScraper()
    mock_html = """
    <html><body>
    <div class="job-listing">Hiring: Sales Development Representative (SDR)</div>
    <div class="job-listing">Hiring: Account Executive</div>
    </body></html>
    """
    with patch.object(scraper, "_fetch_html", new_callable=AsyncMock, return_value=mock_html):
        signals = await scraper.extract_signals("https://acme.com")
    job_signals = [s for s in signals if s.signal_type == "job_posting"]
    assert len(job_signals) >= 1
    assert "SDR" in job_signals[0].text or "Sales Development" in job_signals[0].text


@pytest.mark.asyncio
async def test_extracts_tech_stack():
    scraper = WebsiteScraper()
    mock_html = """<html><head>
    <script src="https://js.hsforms.net/forms/v2.js"></script>
    <script src="https://cdn.segment.com/analytics.js"></script>
    </head></html>"""
    with patch.object(scraper, "_fetch_html", new_callable=AsyncMock, return_value=mock_html):
        signals = await scraper.extract_signals("https://acme.com")
    tech_signals = [s for s in signals if s.signal_type == "tech_stack"]
    assert any("HubSpot" in s.text or "Segment" in s.text for s in tech_signals)
