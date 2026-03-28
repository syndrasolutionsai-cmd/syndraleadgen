import pytest
from leadforge.scraping.base import ProspectRaw, BaseScraper, ScraperSource


def test_prospect_raw_full_name():
    p = ProspectRaw(
        first_name="John",
        last_name="Smith",
        role="CEO",
        company_name="Acme",
        source=ScraperSource.LINKEDIN,
    )
    assert p.full_name == "John Smith"


def test_prospect_raw_defaults():
    p = ProspectRaw(
        first_name="Jane",
        last_name="Doe",
        company_name="Corp",
        source=ScraperSource.HUNTER,
    )
    assert p.email is None
    assert p.enriched_data == {}
    assert p.signals == []


def test_base_scraper_is_abstract():
    with pytest.raises(TypeError):
        BaseScraper()  # Cannot instantiate abstract class
