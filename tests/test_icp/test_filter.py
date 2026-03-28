import pytest
from leadforge.icp.config import ICPConfig
from leadforge.icp.filter import ICPFilter
from leadforge.scraping.aggregator import MergedProspect


def make_icp(**kwargs) -> ICPConfig:
    defaults = {
        "industries": ["SaaS"],
        "roles": ["CEO"],
        "company_size": {"min": 10, "max": 500},
        "geography": ["US"],
        "tech_signals": ["HubSpot"],
        "exclude_signals": ["hiring freeze"],
        "min_icp_score": 70,
    }
    defaults.update(kwargs)
    return ICPConfig(**defaults)


def make_prospect(**kwargs) -> MergedProspect:
    defaults = {
        "first_name": "John",
        "last_name": "Smith",
        "company_name": "Acme",
        "confirmed_sources": ["linkedin", "hunter"],
        "role": "CEO",
        "industry": "SaaS",
        "geography": "US",
        "company_size": 50,
        "tech_stack": ["HubSpot"],
        "enriched_data": {},
    }
    defaults.update(kwargs)
    return MergedProspect(**defaults)


def test_perfect_match_scores_100():
    icp = make_icp()
    prospect = make_prospect()
    f = ICPFilter(icp)
    score = f.score(prospect)
    assert score == 100.0


def test_wrong_role_reduces_score():
    icp = make_icp()
    prospect = make_prospect(role="Intern")
    f = ICPFilter(icp)
    score = f.score(prospect)
    assert score < 70


def test_exclude_signal_in_enriched_data_rejects():
    icp = make_icp()
    prospect = make_prospect(enriched_data={"news": "company announced hiring freeze"})
    f = ICPFilter(icp)
    score = f.score(prospect)
    assert score == 0.0  # exclude signals always → 0


def test_no_geo_filter_passes_all_geographies():
    icp = make_icp(geography=[])
    prospect = make_prospect(geography="BR")
    f = ICPFilter(icp)
    score = f.score(prospect)
    assert score >= 70


def test_filter_removes_below_threshold():
    icp = make_icp(min_icp_score=70)
    f = ICPFilter(icp)
    good = make_prospect()
    bad = make_prospect(role="Intern", geography="BR", tech_stack=[])
    passed = f.filter([good, bad])
    assert len(passed) == 1
    assert passed[0].first_name == "John"
