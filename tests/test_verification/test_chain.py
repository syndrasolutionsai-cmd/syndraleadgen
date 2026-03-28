import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from leadforge.verification.chain import VerificationChain


@pytest.mark.asyncio
async def test_role_based_rejected():
    chain = VerificationChain(zerobounce_key="zb-key", hunter_key="h-key")
    result = await chain.verify("info@acme.com")
    assert result.passed is False
    assert result.rejection_reason == "role_based_address"


@pytest.mark.asyncio
async def test_invalid_syntax_rejected():
    chain = VerificationChain(zerobounce_key="zb-key", hunter_key="h-key")
    result = await chain.verify("not-an-email")
    assert result.passed is False
    assert result.rejection_reason == "invalid_syntax"


@pytest.mark.asyncio
async def test_valid_email_passes_all_stages():
    chain = VerificationChain(zerobounce_key="zb-key", hunter_key="h-key")
    from leadforge.verification.zerobounce import ZeroBounceResult
    with (
        patch("leadforge.verification.chain.check_mx", new_callable=AsyncMock, return_value=True),
        patch("leadforge.verification.chain.check_smtp", new_callable=AsyncMock, return_value=True),
        patch.object(chain.zb, "verify", new_callable=AsyncMock, return_value=ZeroBounceResult(
            is_valid=True, is_catch_all=False, score=9, status="valid"
        )),
        patch("leadforge.verification.chain.verify_with_hunter", new_callable=AsyncMock, return_value=85),
    ):
        result = await chain.verify("john.smith@acme.com")
    assert result.passed is True
    assert result.score > 70
    assert result.rejection_reason is None


@pytest.mark.asyncio
async def test_zerobounce_invalid_rejects():
    chain = VerificationChain(zerobounce_key="zb-key", hunter_key="h-key")
    from leadforge.verification.zerobounce import ZeroBounceResult
    with (
        patch("leadforge.verification.chain.check_mx", new_callable=AsyncMock, return_value=True),
        patch("leadforge.verification.chain.check_smtp", new_callable=AsyncMock, return_value=True),
        patch.object(chain.zb, "verify", new_callable=AsyncMock, return_value=ZeroBounceResult(
            is_valid=False, is_catch_all=False, score=0, status="invalid"
        )),
    ):
        result = await chain.verify("ghost@acme.com")
    assert result.passed is False
    assert "zerobounce" in result.rejection_reason
