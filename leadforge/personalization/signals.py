from dataclasses import dataclass
from pathlib import Path
from leadforge.personalization.claude_client import ask_claude_json
from leadforge.scraping.aggregator import MergedProspect

PROMPT = (Path(__file__).parent / "prompts" / "signal_picker.txt").read_text()

SIGNAL_PRIORITY = ["linkedin_activity", "funding", "job_posting", "tech_stack", "review_pain"]


@dataclass
class SelectedSignal:
    signal_type: str
    signal_text: str
    confidence: float
    why_chosen: str


class SignalPicker:
    async def pick(self, prospect: MergedProspect) -> SelectedSignal:
        """Select the strongest personalization signal for this prospect."""
        if not prospect.signals:
            return SelectedSignal(
                signal_type="generic",
                signal_text=f"{prospect.first_name} is {prospect.role or 'a decision-maker'} at {prospect.company_name}",
                confidence=0.2,
                why_chosen="No specific signals found — using role/company as fallback",
            )

        # Build signals summary for Claude
        signals_summary = "\n".join([
            f"- [{s.signal_type}] {s.text[:300]} (confidence: {s.confidence:.0%})"
            for s in sorted(prospect.signals, key=lambda s: SIGNAL_PRIORITY.index(s.signal_type) if s.signal_type in SIGNAL_PRIORITY else 99)
        ])

        prospect_summary = (
            f"Prospect: {prospect.full_name}, {prospect.role or 'Unknown role'} at {prospect.company_name}\n"
            f"Industry: {prospect.industry or 'Unknown'}\n"
            f"Geography: {prospect.geography or 'Unknown'}\n"
            f"Available signals:\n{signals_summary}"
        )

        result = await ask_claude_json(
            system=PROMPT,
            user=prospect_summary,
            expected_keys=["signal_type", "signal_text", "confidence", "why_chosen"],
            temperature=0.3,
        )
        return SelectedSignal(**result)
