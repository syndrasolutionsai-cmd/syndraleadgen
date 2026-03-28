from dataclasses import dataclass
from pathlib import Path
from leadforge.personalization.claude_client import ask_claude_json

PROMPT = (Path(__file__).parent / "prompts" / "quality_scorer.txt").read_text()
PASS_THRESHOLD = 80


@dataclass
class QualityScore:
    icebreaker_specificity: int
    pain_relevance: int
    value_clarity: int
    cta_quality: int
    human_tone: int
    total_score: int
    notes: str

    @property
    def passes_threshold(self) -> bool:
        return self.total_score >= PASS_THRESHOLD


class QualityScorer:
    async def score(self, email_body: str, subject: str) -> QualityScore:
        user_msg = f"Subject: {subject}\n\nEmail body:\n{email_body}"
        result = await ask_claude_json(
            system=PROMPT,
            user=user_msg,
            expected_keys=["icebreaker_specificity", "pain_relevance", "value_clarity", "cta_quality", "human_tone", "total_score", "notes"],
            temperature=0.1,
        )
        return QualityScore(
            icebreaker_specificity=int(result["icebreaker_specificity"]),
            pain_relevance=int(result["pain_relevance"]),
            value_clarity=int(result["value_clarity"]),
            cta_quality=int(result["cta_quality"]),
            human_tone=int(result["human_tone"]),
            total_score=int(result["total_score"]),
            notes=result["notes"],
        )
