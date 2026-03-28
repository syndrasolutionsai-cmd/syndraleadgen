import json
import re
import anthropic
from leadforge.config import settings

client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
MODEL = "claude-sonnet-4-6"


async def ask_claude_json(
    system: str,
    user: str,
    expected_keys: list[str],
    temperature: float = 0.7,
    max_tokens: int = 1024,
) -> dict:
    """
    Call Claude and parse the response as JSON.
    Raises ValueError if the response cannot be parsed or is missing expected keys.
    """
    message = await client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system,
        messages=[{"role": "user", "content": user}],
    )

    raw = message.content[0].text.strip()

    # Claude sometimes wraps JSON in ```json ... ```
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse Claude response as JSON: {e}\nRaw: {raw[:200]}")

    missing = [k for k in expected_keys if k not in data]
    if missing:
        raise ValueError(f"Claude response missing expected keys: {missing}\nGot: {list(data.keys())}")

    return data


async def ask_claude_text(
    system: str,
    user: str,
    temperature: float = 0.7,
    max_tokens: int = 512,
) -> str:
    """Call Claude and return raw text response."""
    message = await client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return message.content[0].text.strip()
