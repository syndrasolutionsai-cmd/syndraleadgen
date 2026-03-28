from dataclasses import dataclass
from pathlib import Path
from leadforge.personalization.claude_client import ask_claude_json

PROMPT = (Path(__file__).parent / "prompts" / "niche_voice.txt").read_text()


@dataclass
class NicheFraming:
    niche_framing: str
    key_pain: str
    vocabulary_used: list[str]


class NicheVoiceTranslator:
    async def translate(
        self,
        niche: str,
        signal_text: str,
        signal_type: str,
        prospect_role: str,
    ) -> NicheFraming:
        user_msg = (
            f"Niche: {niche}\n"
            f"Prospect role: {prospect_role}\n"
            f"Signal type: {signal_type}\n"
            f"Signal: {signal_text}\n\n"
            "Reframe this for a cold email using exact niche vocabulary."
        )
        result = await ask_claude_json(
            system=PROMPT,
            user=user_msg,
            expected_keys=["niche_framing", "key_pain", "vocabulary_used"],
            temperature=0.5,
        )
        return NicheFraming(**result)
