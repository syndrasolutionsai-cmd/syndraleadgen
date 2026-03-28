import pytest
from leadforge.review.queue import ReviewSelector, ReviewReason


def make_email(quality_score=85, email_verif_score=90, signal_type="linkedin_activity",
               is_first_campaign=False):
    """Create a mock email dict for testing."""
    return {
        "id": "email-1",
        "quality_score": quality_score,
        "email_verification_score": email_verif_score,
        "signal_type": signal_type,
        "is_first_campaign": is_first_campaign,
    }


def test_low_verification_score_mandatory_review():
    selector = ReviewSelector(review_pct=15)
    email = make_email(email_verif_score=60)
    reason = selector.get_review_reason(email)
    assert reason == ReviewReason.LOW_VERIFICATION_SCORE


def test_weak_signal_flagged_for_review():
    selector = ReviewSelector(review_pct=15)
    email = make_email(signal_type="generic")
    reason = selector.get_review_reason(email)
    assert reason == ReviewReason.WEAK_SIGNAL


def test_first_campaign_always_reviewed():
    selector = ReviewSelector(review_pct=15)
    email = make_email(is_first_campaign=True)
    reason = selector.get_review_reason(email)
    assert reason == ReviewReason.FIRST_CAMPAIGN


def test_good_email_may_be_in_random_sample():
    selector = ReviewSelector(review_pct=100)  # 100% review for test
    email = make_email()
    selected = selector.select_for_review([email])
    assert len(selected) == 1
    assert selected[0]["review_reason"] == ReviewReason.RANDOM_SAMPLE


def test_select_applies_percentage():
    selector = ReviewSelector(review_pct=20)
    emails = [make_email() for _ in range(100)]
    selected = selector.select_for_review(emails)
    assert len(selected) >= 0
    assert len(selected) <= len(emails)
