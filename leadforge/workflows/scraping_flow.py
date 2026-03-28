# leadforge/workflows/scraping_flow.py
import uuid
from prefect import flow, task, get_run_logger

from leadforge.scraping.linkedin import LinkedInScraper
from leadforge.scraping.hunter import HunterScraper
from leadforge.scraping.clearbit import ClearbitScraper
from leadforge.scraping.website import WebsiteScraper
from leadforge.scraping.google_news import GoogleNewsScraper
from leadforge.scraping.review_sites import ReviewSitesScraper
from leadforge.scraping.aggregator import Aggregator
from leadforge.icp.config import ICPConfig
from leadforge.icp.filter import ICPFilter
from leadforge.config import settings


@task(retries=2, retry_delay_seconds=30, name="scrape-linkedin")
async def scrape_linkedin(icp_config: dict, campaign_id: str, limit: int):
    scraper = LinkedInScraper(api_token=settings.apify_api_token)
    return await scraper.search(icp_config, campaign_id, limit)


@task(retries=2, retry_delay_seconds=10, name="enrich-clearbit")
async def enrich_with_clearbit(emails: list[str]):
    scraper = ClearbitScraper(api_key=settings.clearbit_api_key)
    results = []
    for email in emails:
        prospect = await scraper.enrich(email)
        if prospect:
            results.append(prospect)
    return results


@task(name="aggregate-and-filter")
async def aggregate_and_filter(all_raw: list, icp_config_dict: dict) -> list:
    aggregator = Aggregator(min_sources=2)
    merged = aggregator.aggregate(all_raw)

    icp = ICPConfig(
        industries=icp_config_dict.get("industries", []),
        roles=icp_config_dict.get("roles", []),
        company_size=icp_config_dict.get("company_size", {"min": 1, "max": 10_000}),
        geography=icp_config_dict.get("geography", []),
        tech_signals=icp_config_dict.get("tech_signals", []),
        exclude_signals=icp_config_dict.get("exclude_signals", []),
        min_icp_score=float(icp_config_dict.get("min_icp_score", 70)),
    )
    icp_filter = ICPFilter(icp)
    return icp_filter.filter(merged)


@flow(name="scraping-flow", log_prints=True)
async def run_scraping_flow(campaign_id: str, icp_config: dict, batch_size: int) -> list:
    logger = get_run_logger()
    logger.info(f"Starting scraping for campaign {campaign_id}, target: {batch_size} prospects")

    linkedin_results = await scrape_linkedin(icp_config, campaign_id, batch_size * 3)
    logger.info(f"LinkedIn: {len(linkedin_results)} raw prospects")

    all_raw = linkedin_results
    filtered = await aggregate_and_filter(all_raw, icp_config)
    logger.info(f"After aggregation + ICP filter: {len(filtered)} prospects")

    return filtered[:batch_size]
