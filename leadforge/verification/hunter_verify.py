import httpx


async def verify_with_hunter(email: str, api_key: str) -> int:
    """
    Verify an email with Hunter.io and return a confidence score 0-100.
    Returns 0 on error or invalid result.
    """
    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            resp = await client.get(
                "https://api.hunter.io/v2/email-verifier",
                params={"email": email, "api_key": api_key},
            )
            resp.raise_for_status()
            data = resp.json().get("data", {})
            result = data.get("result", "unverifiable")
            score = data.get("score", 0)
            if result == "undeliverable":
                return 0
            return int(score)
        except Exception:
            return 50  # uncertain — don't reject
