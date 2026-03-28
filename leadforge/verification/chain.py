from dataclasses import dataclass

from leadforge.verification.syntax import check_syntax, is_role_based
from leadforge.verification.mx_check import check_mx
from leadforge.verification.smtp_check import check_smtp
from leadforge.verification.zerobounce import ZeroBounceVerifier
from leadforge.verification.hunter_verify import verify_with_hunter


@dataclass
class VerificationResult:
    email: str
    passed: bool
    score: float       # 0-100 composite score
    is_catch_all: bool
    rejection_reason: str | None  # None if passed


class VerificationChain:
    def __init__(self, zerobounce_key: str, hunter_key: str):
        self.zb = ZeroBounceVerifier(zerobounce_key)
        self.hunter_key = hunter_key

    async def verify(self, email: str) -> VerificationResult:
        email = email.strip().lower()

        # Step 1: Syntax
        if not check_syntax(email):
            return VerificationResult(email=email, passed=False, score=0, is_catch_all=False, rejection_reason="invalid_syntax")

        # Step 2: Role-based
        if is_role_based(email):
            return VerificationResult(email=email, passed=False, score=0, is_catch_all=False, rejection_reason="role_based_address")

        domain = email.split("@")[1]

        # Step 3: MX record
        if not await check_mx(domain):
            return VerificationResult(email=email, passed=False, score=0, is_catch_all=False, rejection_reason="no_mx_record")

        # Step 4: SMTP handshake
        smtp_ok = await check_smtp(email)
        if not smtp_ok:
            return VerificationResult(email=email, passed=False, score=10, is_catch_all=False, rejection_reason="smtp_rejected")

        # Step 5: ZeroBounce
        zb_result = await self.zb.verify(email)
        if not zb_result.is_valid:
            return VerificationResult(email=email, passed=False, score=0, is_catch_all=False, rejection_reason=f"zerobounce:{zb_result.status}")

        # Step 6: Hunter verification
        hunter_score = await verify_with_hunter(email, self.hunter_key)
        if hunter_score < 30:
            return VerificationResult(email=email, passed=False, score=hunter_score, is_catch_all=zb_result.is_catch_all, rejection_reason="hunter_low_confidence")

        # Composite score: ZeroBounce score (0-10 → 0-50) + Hunter score (0-100 → 0-50)
        composite = (zb_result.score / 10 * 50) + (hunter_score / 100 * 50)
        return VerificationResult(
            email=email,
            passed=True,
            score=round(composite, 1),
            is_catch_all=zb_result.is_catch_all,
            rejection_reason=None,
        )
