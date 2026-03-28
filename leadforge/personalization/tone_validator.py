from dataclasses import dataclass
from pathlib import Path
from leadforge.personalization.claude_client import ask_claude_json

PROMPT = (Path(__file__).parent / "prompts" / "tone_validator.txt").read_text()

# Local pre-screen: catch obvious fails before spending Claude tokens
LOCAL_BANNED = [
    "i hope this finds you well",
    "i came across your profile",
    "i wanted to reach out",
    "my name is",
    "i work at",
    "let's hop on a",
    "are you free this week",
    "book a demo",
    "schedule a meeting",
    "revolutionary",
    "game-changing",
    "best-in-class",
    "cutting-edge",
    "seamlessly",
    "transformative",
    "synergy",
]


def has_local_hard_fails(email_body: str) -> bool:
    """Fast local check before calling Claude."""
    lower = email_body.lower()
    return any(banned in lower for banned in LOCAL_BANNED)


@dataclass
class ValidationResult:
    passed: bool
    hard_fails: list[str]
    warnings: list[str]
    verdict: str


class ToneValidator:
    async def validate(self, email_body: str) -> ValidationResult:
        """Validate email tone. Returns ValidationResult."""
        # Local pre-screen — saves Claude tokens on obvious fails
        if has_local_hard_fails(email_body):
            matching = [b for b in LOCAL_BANNED if b in email_body.lower()]
            return ValidationResult(
                passed=False,
                hard_fails=[f"Banned phrase detected: '{matching[0]}'"],
                warnings=[],
                verdict=f"Local pre-screen failed on: {matching[0]}",
            )

        result = await ask_claude_json(
            system=PROMPT,
            user=f"Email to review:\n\n{email_body}",
            expected_keys=["passed", "hard_fails", "warnings", "verdict"],
            temperature=0.1,
        )
        return ValidationResult(
            passed=bool(result["passed"]),
            hard_fails=result.get("hard_fails", []),
            warnings=result.get("warnings", []),
            verdict=result.get("verdict", ""),
        )
