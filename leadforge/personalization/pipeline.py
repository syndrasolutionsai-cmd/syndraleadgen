from dataclasses import dataclass
from leadforge.personalization.signals import SignalPicker
from leadforge.personalization.niche_voice import NicheVoiceTranslator
from leadforge.personalization.icebreaker import IcebreakerGenerator
from leadforge.personalization.email_writer import EmailWriter
from leadforge.personalization.tone_validator import ToneValidator
from leadforge.personalization.quality_scorer import QualityScorer, PASS_THRESHOLD
from leadforge.scraping.aggregator import MergedProspect

MAX_ATTEMPTS = 3


@dataclass
class PersonalizedEmail:
    subject: str
    body: str
    icebreaker: str
    signal_type: str
    signal_text: str
    quality_score: int
    attempts: int
    flagged_for_manual: bool = False


class PersonalizationPipeline:
    def __init__(self, niche: str, value_prop: str, language: str = "en"):
        self.niche = niche
        self.value_prop = value_prop
        self.language = language
        self.signal_picker = SignalPicker()
        self.niche_voice = NicheVoiceTranslator()
        self.icebreaker_gen = IcebreakerGenerator()
        self.email_writer = EmailWriter()
        self.tone_validator = ToneValidator()
        self.quality_scorer = QualityScorer()

    async def personalize(self, prospect: MergedProspect) -> PersonalizedEmail:
        """
        Run the full 6-layer personalization pipeline.
        Retries up to MAX_ATTEMPTS on quality failures.
        Flags prospect for manual writing after max retries.
        """
        # Layer 1: Signal selection (done once — same signal across retries)
        selected_signal = await self.signal_picker.pick(prospect)

        # Layer 2: Niche voice translation (done once)
        niche_framing = await self.niche_voice.translate(
            niche=self.niche,
            signal_text=selected_signal.signal_text,
            signal_type=selected_signal.signal_type,
            prospect_role=prospect.role or "decision-maker",
        )

        last_result = None
        for attempt in range(1, MAX_ATTEMPTS + 1):
            # Layer 3: Icebreaker (re-run on retry for variation)
            icebreaker = await self.icebreaker_gen.generate(
                prospect_name=prospect.first_name,
                company_name=prospect.company_name,
                signal_type=selected_signal.signal_type,
                signal_text=selected_signal.signal_text,
                niche_framing=niche_framing.niche_framing,
                niche=self.niche,
            )

            # Layer 4: Email writing
            draft = await self.email_writer.write(
                icebreaker=icebreaker.text,
                key_pain=niche_framing.key_pain,
                company_value_prop=self.value_prop,
                prospect_name=prospect.first_name,
                language=self.language,
            )

            # Layer 5: Tone validation
            tone_result = await self.tone_validator.validate(draft.body)
            if not tone_result.passed:
                continue  # retry — don't bother scoring a failing email

            # Layer 6: Quality scoring
            quality = await self.quality_scorer.score(draft.body, draft.subject)

            last_result = PersonalizedEmail(
                subject=draft.subject,
                body=draft.body,
                icebreaker=icebreaker.text,
                signal_type=selected_signal.signal_type,
                signal_text=selected_signal.signal_text,
                quality_score=quality.total_score,
                attempts=attempt,
            )

            if quality.passes_threshold:
                return last_result
            # else: retry

        # All attempts failed — flag for manual writing
        if last_result:
            last_result.flagged_for_manual = True
            last_result.attempts = MAX_ATTEMPTS
            return last_result

        # Edge case: tone validator failed all 3 times
        return PersonalizedEmail(
            subject="",
            body="",
            icebreaker="",
            signal_type=selected_signal.signal_type,
            signal_text=selected_signal.signal_text,
            quality_score=0,
            attempts=MAX_ATTEMPTS,
            flagged_for_manual=True,
        )
