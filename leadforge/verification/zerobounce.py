import httpx
from dataclasses import dataclass


@dataclass
class ZeroBounceResult:
    is_valid: bool
    is_catch_all: bool
    score: int  # 0-10 ZeroBounce quality score
    status: str  # valid, invalid, catch-all, spamtrap, abuse, do_not_mail, unknown


class ZeroBounceVerifier:
    BASE_URL = "https://api.zerobounce.net/v2"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def verify(self, email: str) -> ZeroBounceResult:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(
                f"{self.BASE_URL}/validate",
                params={"api_key": self.api_key, "email": email},
            )
            resp.raise_for_status()
            data = resp.json()

        status = data.get("status", "unknown")
        is_valid = status == "valid"
        is_catch_all = status == "catch-all"
        score_resp = await self._get_score(email)

        return ZeroBounceResult(
            is_valid=is_valid or is_catch_all,
            is_catch_all=is_catch_all,
            score=score_resp,
            status=status,
        )

    async def _get_score(self, email: str) -> int:
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.get(
                    f"{self.BASE_URL}/getscore",
                    params={"api_key": self.api_key, "email": email},
                )
                resp.raise_for_status()
                return int(resp.json().get("score", 5))
        except Exception:
            return 5  # default to mid score on failure
