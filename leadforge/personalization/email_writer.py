from dataclasses import dataclass
from pathlib import Path
from leadforge.personalization.claude_client import ask_claude_json

PROMPT = (Path(__file__).parent / "prompts" / "email_writer.txt").read_text()
MAX_WORDS = 130


@dataclass
class DraftEmail:
    subject: str
    body: str
    word_count: int

    @property
    def over_limit(self) -> bool:
        return self.word_count > MAX_WORDS


class EmailWriter:
    async def write(
        self,
        icebreaker: str,
        key_pain: str,
        company_value_prop: str,
        prospect_name: str,
        language: str = "en",
    ) -> DraftEmail:
        user_msg = (
            f"Prospect first name: {prospect_name}\n"
            f"Language: {language}\n"
            f"Icebreaker (use this EXACTLY as the opening): {icebreaker}\n"
            f"Key pain to address: {key_pain}\n"
            f"Value proposition: {company_value_prop}\n\n"
            "Write the complete cold email."
        )
        result = await ask_claude_json(
            system=PROMPT,
            user=user_msg,
            expected_keys=["subject", "body", "word_count"],
            temperature=0.7,
        )
        actual_count = len(result["body"].split())
        return DraftEmail(
            subject=result["subject"],
            body=result["body"],
            word_count=actual_count,
        )
