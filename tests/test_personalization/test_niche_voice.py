import pytest
from unittest.mock import AsyncMock, patch
from leadforge.personalization.niche_voice import NicheVoiceTranslator, NicheFraming


@pytest.mark.asyncio
async def test_niche_voice_returns_framing():
    translator = NicheVoiceTranslator()
    mock_response = {
        "niche_framing": "When you posted about hitting 1M ARR, your CAC must be front of mind.",
        "key_pain": "scaling outbound without hiring more SDRs",
        "vocabulary_used": ["ARR", "CAC", "SDRs"],
    }
    with patch("leadforge.personalization.niche_voice.ask_claude_json", new_callable=AsyncMock, return_value=mock_response):
        result = await translator.translate(
            niche="B2B SaaS",
            signal_text="Just posted about hitting 1M ARR",
            signal_type="linkedin_activity",
            prospect_role="CEO",
        )
    assert isinstance(result, NicheFraming)
    assert "ARR" in result.niche_framing or "ARR" in str(result.vocabulary_used)
    assert result.key_pain != ""
