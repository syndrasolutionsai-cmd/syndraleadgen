import pytest
from unittest.mock import AsyncMock, patch
from leadforge.personalization.signals import SignalPicker, SelectedSignal
from leadforge.scraping.base import Signal, ScraperSource
from leadforge.scraping.aggregator import MergedProspect


def make_prospect_with_signals(signals):
    p = MergedProspect(
        first_name="John", last_name="Smith", company_name="Acme",
        confirmed_sources=["linkedin", "hunter"]
    )
    p.signals = signals
    return p


@pytest.mark.asyncio
async def test_picks_linkedin_over_tech_stack():
    picker = SignalPicker()
    p = make_prospect_with_signals([
        Signal("linkedin_activity", "Just posted about hitting 1M ARR", ScraperSource.LINKEDIN, confidence=0.95),
        Signal("tech_stack", "Uses HubSpot", ScraperSource.CLEARBIT, confidence=0.85),
    ])
    mock_response = {
        "signal_type": "linkedin_activity",
        "signal_text": "Just posted about hitting 1M ARR",
        "confidence": 0.95,
        "why_chosen": "Recent milestone post is highly specific and recent.",
    }
    with patch("leadforge.personalization.signals.ask_claude_json", new_callable=AsyncMock, return_value=mock_response):
        result = await picker.pick(p)
    assert isinstance(result, SelectedSignal)
    assert result.signal_type == "linkedin_activity"


@pytest.mark.asyncio
async def test_no_signals_returns_fallback():
    picker = SignalPicker()
    p = make_prospect_with_signals([])
    result = await picker.pick(p)
    assert result.signal_type == "generic"
    assert result.confidence < 0.5
