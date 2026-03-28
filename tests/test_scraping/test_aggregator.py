import pytest
from leadforge.scraping.aggregator import Aggregator, merge_prospect_data
from leadforge.scraping.base import ProspectRaw, ScraperSource, Signal


def make_prospect(first="John", last="Smith", company="Acme", source=ScraperSource.LINKEDIN, email=None):
    return ProspectRaw(first_name=first, last_name=last, company_name=company, source=source, email=email)


def test_merge_two_sources_confirms_prospect():
    linkedin = make_prospect(source=ScraperSource.LINKEDIN)
    hunter = make_prospect(source=ScraperSource.HUNTER, email="john@acme.com")
    merged = merge_prospect_data([linkedin, hunter])
    assert len(merged.confirmed_sources) == 2
    assert merged.email == "john@acme.com"


def test_single_source_not_confirmed():
    linkedin = make_prospect(source=ScraperSource.LINKEDIN)
    merged = merge_prospect_data([linkedin])
    assert len(merged.confirmed_sources) == 1
    assert merged.is_confirmed is False


def test_aggregator_filters_unconfirmed(monkeypatch):
    agg = Aggregator(min_sources=2)
    # Two sources for John, one for Jane
    john_l = make_prospect("John", "Smith", "Acme", ScraperSource.LINKEDIN)
    john_h = make_prospect("John", "Smith", "Acme", ScraperSource.HUNTER, "john@acme.com")
    jane_l = make_prospect("Jane", "Doe", "Corp", ScraperSource.LINKEDIN)

    confirmed = agg.filter_confirmed([
        merge_prospect_data([john_l, john_h]),
        merge_prospect_data([jane_l]),
    ])
    assert len(confirmed) == 1
    assert confirmed[0].first_name == "John"


def test_signals_merged_from_all_sources():
    sig1 = Signal("linkedin_activity", "Hit 1M ARR", ScraperSource.LINKEDIN)
    sig2 = Signal("tech_stack", "Uses HubSpot", ScraperSource.CLEARBIT)
    p1 = make_prospect(source=ScraperSource.LINKEDIN)
    p1.signals = [sig1]
    p2 = make_prospect(source=ScraperSource.CLEARBIT)
    p2.signals = [sig2]
    merged = merge_prospect_data([p1, p2])
    assert len(merged.signals) == 2
