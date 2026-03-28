import pytest
from unittest.mock import AsyncMock, patch
from leadforge.personalization.icebreaker import IcebreakerGenerator, Icebreaker


@pytest.mark.asyncio
async def test_returns_best_variant():
    gen = IcebreakerGenerator()
    mock_response = {
        "variants": [
            {"text": "Your post about 1M ARR — that inflection point is where CAC starts fighting LTV.", "specificity_score": 0.9, "surprise_factor": 0.85},
            {"text": "The 1M ARR milestone usually brings the outbound scaling question.", "specificity_score": 0.75, "surprise_factor": 0.7},
            {"text": "Congrats on the 1M ARR — that growth stage changes everything about acquisition.", "specificity_score": 0.6, "surprise_factor": 0.5},
        ]
    }
    with patch("leadforge.personalization.icebreaker.ask_claude_json", new_callable=AsyncMock, return_value=mock_response):
        result = await gen.generate(
            prospect_name="John Smith",
            company_name="Acme",
            signal_type="linkedin_activity",
            signal_text="Just posted about hitting 1M ARR",
            niche_framing="Your post about 1M ARR is where CAC vs LTV tension appears",
            niche="B2B SaaS",
        )
    assert isinstance(result, Icebreaker)
    # Should pick the highest combined score (specificity + surprise)
    assert result.text == mock_response["variants"][0]["text"]
    assert result.specificity_score == 0.9


@pytest.mark.asyncio
async def test_does_not_start_with_i():
    gen = IcebreakerGenerator()
    mock_response = {
        "variants": [
            {"text": "I saw your post about 1M ARR.", "specificity_score": 0.5, "surprise_factor": 0.5},
            {"text": "Your post about 1M ARR speaks to the scaling challenge.", "specificity_score": 0.8, "surprise_factor": 0.75},
            {"text": "The 1M ARR milestone you shared — growth at that stage changes everything.", "specificity_score": 0.7, "surprise_factor": 0.7},
        ]
    }
    with patch("leadforge.personalization.icebreaker.ask_claude_json", new_callable=AsyncMock, return_value=mock_response):
        result = await gen.generate("John", "Acme", "linkedin_activity", "1M ARR post", "framing", "SaaS")
    # Should not pick the "I saw" variant even if it scored high
    assert not result.text.startswith("I ")
