from dataclasses import dataclass
from pathlib import Path
from leadforge.personalization.claude_client import ask_claude_json

PROMPT = (Path(__file__).parent / "prompts" / "icebreaker.txt").read_text()

BANNED_OPENERS = ["i ", "we ", "our ", "i'd ", "i've ", "i'm ", "i hope", "i came", "i saw", "i noticed"]


@dataclass
class Icebreaker:
    text: str
    specificity_score: float
    surprise_factor: float


class IcebreakerGenerator:
    async def generate(
        self,
        prospect_name: str,
        company_name: str,
        signal_type: str,
        signal_text: str,
        niche_framing: str,
        niche: str,
    ) -> Icebreaker:
        user_msg = (
            f"Prospect: {prospect_name} at {company_name}\n"
            f"Niche: {niche}\n"
            f"Signal type: {signal_type}\n"
            f"Signal: {signal_text}\n"
            f"Niche framing context: {niche_framing}\n\n"
            "Write 3 icebreaker variants."
        )
        result = await ask_claude_json(
            system=PROMPT,
            user=user_msg,
            expected_keys=["variants"],
            temperature=0.8,
        )
        variants = result["variants"]

        # Filter out banned openers
        valid = [v for v in variants if not any(v["text"].lower().startswith(b) for b in BANNED_OPENERS)]
        if not valid:
            valid = variants  # fallback: use all if all were filtered

        # Pick highest combined score
        best = max(valid, key=lambda v: v["specificity_score"] + v["surprise_factor"])
        return Icebreaker(
            text=best["text"],
            specificity_score=best["specificity_score"],
            surprise_factor=best["surprise_factor"],
        )
