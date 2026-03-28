from leadforge.niche.intelligence import NicheScorer, NicheScore


def test_scores_multiple_niches():
    scorer = NicheScorer()
    scores = scorer.rank_niches([
        "B2B SaaS",
        "Legal Tech",
        "Marketing Agencies",
        "Management Consulting",
    ])
    assert len(scores) == 4
    assert all(isinstance(s, NicheScore) for s in scores)
    # All scores should be in valid range
    for s in scores:
        assert 0 <= s.total_score <= 100


def test_returns_sorted_by_score():
    scorer = NicheScorer()
    scores = scorer.rank_niches(["B2B SaaS", "Legal Tech"])
    assert scores[0].total_score >= scores[1].total_score


def test_report_contains_recommendation():
    scorer = NicheScorer()
    scores = scorer.rank_niches(["B2B SaaS", "Legal Tech"])
    report = scorer.generate_report(scores)
    assert "Recommended" in report or "recommended" in report
    assert "B2B SaaS" in report or "Legal Tech" in report
