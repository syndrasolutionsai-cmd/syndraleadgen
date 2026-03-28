import random
from enum import Enum
from typing import Any


class ReviewReason(str, Enum):
    LOW_VERIFICATION_SCORE = "low_verification_score"
    WEAK_SIGNAL = "weak_signal"
    FIRST_CAMPAIGN = "first_campaign"
    RANDOM_SAMPLE = "random_sample"


WEAK_SIGNAL_TYPES = {"generic", "tech_stack"}
LOW_VERIFICATION_THRESHOLD = 70


class ReviewSelector:
    def __init__(self, review_pct: float = 15.0):
        self.review_pct = review_pct  # percentage 0-100

    def get_review_reason(self, email: dict[str, Any]) -> ReviewReason | None:
        """
        Returns the review reason if this email should be reviewed, or None.
        Mandatory reasons always win over random sampling.
        """
        verif_score = email.get("email_verification_score") or 100
        if verif_score < LOW_VERIFICATION_THRESHOLD:
            return ReviewReason.LOW_VERIFICATION_SCORE

        if email.get("signal_type") in WEAK_SIGNAL_TYPES:
            return ReviewReason.WEAK_SIGNAL

        if email.get("is_first_campaign"):
            return ReviewReason.FIRST_CAMPAIGN

        return None  # candidate for random sample

    def select_for_review(self, emails: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Select emails for human review:
        1. All mandatory reviews (low verif, weak signal, first campaign)
        2. Random sample from the remainder to hit the configured percentage
        """
        mandatory = []
        candidates = []

        for email in emails:
            reason = self.get_review_reason(email)
            if reason is not None:
                email["review_reason"] = reason
                mandatory.append(email)
            else:
                candidates.append(email)

        # Random sample from non-mandatory to hit target percentage
        target_count = max(0, int(len(emails) * self.review_pct / 100) - len(mandatory))
        sample_size = min(target_count, len(candidates))
        sample = random.sample(candidates, sample_size) if sample_size > 0 else []
        for e in sample:
            e["review_reason"] = ReviewReason.RANDOM_SAMPLE

        return mandatory + sample
