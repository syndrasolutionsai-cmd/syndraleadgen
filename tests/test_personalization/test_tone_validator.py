import pytest
from unittest.mock import AsyncMock, patch
from leadforge.personalization.tone_validator import ToneValidator, ValidationResult


@pytest.mark.asyncio
async def test_valid_email_passes():
    validator = ToneValidator()
    mock_response = {
        "passed": True,
        "hard_fails": [],
        "warnings": [],
        "verdict": "Clean, human email with specific icebreaker and soft CTA.",
    }
    with patch("leadforge.personalization.tone_validator.ask_claude_json", new_callable=AsyncMock, return_value=mock_response):
        result = await validator.validate("Good email body here")
    assert result.passed is True
    assert result.hard_fails == []


@pytest.mark.asyncio
async def test_generic_opener_fails():
    validator = ToneValidator()
    mock_response = {
        "passed": False,
        "hard_fails": ["Generic opener: 'I hope this finds you well'"],
        "warnings": [],
        "verdict": "Failed: contains banned generic opener.",
    }
    with patch("leadforge.personalization.tone_validator.ask_claude_json", new_callable=AsyncMock, return_value=mock_response):
        result = await validator.validate("I hope this finds you well. I noticed your company...")
    assert result.passed is False
    assert len(result.hard_fails) > 0


def test_local_banned_phrase_detection():
    """Pre-screen locally before calling Claude to save tokens."""
    from leadforge.personalization.tone_validator import has_local_hard_fails
    assert has_local_hard_fails("I hope this finds you well, John.") is True
    assert has_local_hard_fails("I came across your profile on LinkedIn") is True
    assert has_local_hard_fails("revolutionary platform") is True
    assert has_local_hard_fails("Your post about 1M ARR caught my attention.") is False
