import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from leadforge.personalization.pipeline import PersonalizationPipeline, PersonalizedEmail
from leadforge.scraping.aggregator import MergedProspect
from leadforge.scraping.base import Signal, ScraperSource


def make_prospect():
    p = MergedProspect(
        first_name="John", last_name="Smith", company_name="Acme",
        confirmed_sources=["linkedin", "hunter"],
        role="CEO", industry="B2B SaaS", geography="US",
    )
    p.signals = [Signal("linkedin_activity", "Hit 1M ARR", ScraperSource.LINKEDIN, 0.95)]
    return p


@pytest.mark.asyncio
async def test_pipeline_succeeds_on_first_attempt():
    pipeline = PersonalizationPipeline(niche="B2B SaaS", value_prop="We help SaaS scale outbound")

    with (
        patch.object(pipeline.signal_picker, "pick", new_callable=AsyncMock) as mock_signal,
        patch.object(pipeline.niche_voice, "translate", new_callable=AsyncMock) as mock_voice,
        patch.object(pipeline.icebreaker_gen, "generate", new_callable=AsyncMock) as mock_ice,
        patch.object(pipeline.email_writer, "write", new_callable=AsyncMock) as mock_write,
        patch.object(pipeline.tone_validator, "validate", new_callable=AsyncMock) as mock_tone,
        patch.object(pipeline.quality_scorer, "score", new_callable=AsyncMock) as mock_score,
    ):
        from leadforge.personalization.signals import SelectedSignal
        from leadforge.personalization.niche_voice import NicheFraming
        from leadforge.personalization.icebreaker import Icebreaker
        from leadforge.personalization.email_writer import DraftEmail
        from leadforge.personalization.tone_validator import ValidationResult
        from leadforge.personalization.quality_scorer import QualityScore

        mock_signal.return_value = SelectedSignal("linkedin_activity", "Hit 1M ARR", 0.95, "Recent milestone")
        mock_voice.return_value = NicheFraming("CAC vs LTV framing", "scaling outbound", ["ARR", "CAC"])
        mock_ice.return_value = Icebreaker("Your 1M ARR post — that's where CAC tension appears.", 0.9, 0.85)
        mock_write.return_value = DraftEmail("Scaling outbound past 1M ARR", "Full email body here with 50+ words", 52)
        mock_tone.return_value = ValidationResult(True, [], [], "Clean email")
        mock_score.return_value = QualityScore(18, 17, 16, 18, 17, 86, "Strong email")

        result = await pipeline.personalize(make_prospect())

    assert isinstance(result, PersonalizedEmail)
    assert result.quality_score == 86
    assert result.attempts == 1


@pytest.mark.asyncio
async def test_pipeline_retries_on_low_quality():
    pipeline = PersonalizationPipeline(niche="B2B SaaS", value_prop="We help SaaS scale outbound")

    call_count = 0

    async def mock_score_fn(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        from leadforge.personalization.quality_scorer import QualityScore
        score = 45 if call_count < 3 else 85
        return QualityScore(10, 10, 8, 8, 9, score, "notes")

    with (
        patch.object(pipeline.signal_picker, "pick", new_callable=AsyncMock) as mock_signal,
        patch.object(pipeline.niche_voice, "translate", new_callable=AsyncMock) as mock_voice,
        patch.object(pipeline.icebreaker_gen, "generate", new_callable=AsyncMock) as mock_ice,
        patch.object(pipeline.email_writer, "write", new_callable=AsyncMock) as mock_write,
        patch.object(pipeline.tone_validator, "validate", new_callable=AsyncMock) as mock_tone,
        patch.object(pipeline.quality_scorer, "score", side_effect=mock_score_fn),
    ):
        from leadforge.personalization.signals import SelectedSignal
        from leadforge.personalization.niche_voice import NicheFraming
        from leadforge.personalization.icebreaker import Icebreaker
        from leadforge.personalization.email_writer import DraftEmail
        from leadforge.personalization.tone_validator import ValidationResult

        mock_signal.return_value = SelectedSignal("linkedin_activity", "Hit 1M ARR", 0.95, "reason")
        mock_voice.return_value = NicheFraming("framing", "pain", [])
        mock_ice.return_value = Icebreaker("icebreaker text here", 0.8, 0.8)
        mock_write.return_value = DraftEmail("subject", "email body here", 50)
        mock_tone.return_value = ValidationResult(True, [], [], "ok")

        result = await pipeline.personalize(make_prospect())

    assert result.attempts == 3
    assert result.quality_score == 85
