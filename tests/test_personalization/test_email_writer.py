import pytest
from unittest.mock import AsyncMock, patch
from leadforge.personalization.email_writer import EmailWriter, DraftEmail


@pytest.mark.asyncio
async def test_email_writer_returns_draft():
    writer = EmailWriter()
    mock_response = {
        "subject": "Scaling outbound past 1M ARR",
        "body": "Your post about 1M ARR — that inflection point is where CAC starts fighting LTV. Most SaaS founders at that stage are trying to scale outbound without tripling their SDR headcount. We've helped 12 companies in that exact spot add $400K ARR through cold email without a single new hire. Worth a quick look?",
        "word_count": 52,
    }
    with patch("leadforge.personalization.email_writer.ask_claude_json", new_callable=AsyncMock, return_value=mock_response):
        result = await writer.write(
            icebreaker="Your post about 1M ARR — that inflection point is where CAC starts fighting LTV.",
            key_pain="scaling outbound without more SDRs",
            company_value_prop="We help SaaS companies add pipeline through cold email without new hires",
            prospect_name="John",
            language="en",
        )
    assert isinstance(result, DraftEmail)
    assert result.subject != ""
    assert len(result.body) > 50


@pytest.mark.asyncio
async def test_email_word_count_under_130():
    writer = EmailWriter()
    long_body = " ".join(["word"] * 200)
    mock_response = {"subject": "Test", "body": long_body, "word_count": 200}
    with patch("leadforge.personalization.email_writer.ask_claude_json", new_callable=AsyncMock, return_value=mock_response):
        result = await writer.write("icebreaker", "pain", "value prop", "John", "en")
    # Writer should flag word count issue
    assert result.word_count == 200
    assert result.over_limit is True
