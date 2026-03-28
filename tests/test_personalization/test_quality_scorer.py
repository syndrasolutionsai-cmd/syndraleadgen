import pytest
from unittest.mock import AsyncMock, patch
from leadforge.personalization.quality_scorer import QualityScorer, QualityScore


@pytest.mark.asyncio
async def test_high_quality_email_scores_above_80():
    scorer = QualityScorer()
    mock_response = {
        "icebreaker_specificity": 18,
        "pain_relevance": 17,
        "value_clarity": 16,
        "cta_quality": 18,
        "human_tone": 17,
        "total_score": 86,
        "notes": "Strong icebreaker, slightly generic value prop.",
    }
    with patch("leadforge.personalization.quality_scorer.ask_claude_json", new_callable=AsyncMock, return_value=mock_response):
        result = await scorer.score("Great personalized email body here", "Scaling outbound past 1M ARR")
    assert isinstance(result, QualityScore)
    assert result.total_score == 86
    assert result.passes_threshold is True


@pytest.mark.asyncio
async def test_low_quality_email_fails_threshold():
    scorer = QualityScorer()
    mock_response = {
        "icebreaker_specificity": 8,
        "pain_relevance": 10,
        "value_clarity": 8,
        "cta_quality": 10,
        "human_tone": 9,
        "total_score": 45,
        "notes": "Generic icebreaker, vague pain, aggressive CTA.",
    }
    with patch("leadforge.personalization.quality_scorer.ask_claude_json", new_callable=AsyncMock, return_value=mock_response):
        result = await scorer.score("Generic template email", "Subject line")
    assert result.total_score == 45
    assert result.passes_threshold is False
