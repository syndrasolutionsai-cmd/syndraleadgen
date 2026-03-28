# leadforge/workflows/pipeline_flow.py
import uuid
from prefect import flow, task, get_run_logger
from sqlalchemy.ext.asyncio import AsyncSession

from leadforge.workflows.scraping_flow import run_scraping_flow
from leadforge.verification.chain import VerificationChain
from leadforge.personalization.pipeline import PersonalizationPipeline
from leadforge.review.queue import ReviewSelector
from leadforge.models.prospect import Prospect
from leadforge.models.email import Email, EmailStatus
from leadforge.scraping.aggregator import MergedProspect
from leadforge.config import settings


@task(name="verify-emails", retries=1)
async def verify_emails(prospects: list[MergedProspect]) -> list[tuple]:
    """Verify emails for all prospects. Returns list of (prospect, verification_result)."""
    chain = VerificationChain(
        zerobounce_key=settings.zerobounce_api_key,
        hunter_key=settings.hunter_api_key,
    )
    results = []
    for prospect in prospects:
        if not prospect.email:
            continue
        result = await chain.verify(prospect.email)
        if result.passed:
            results.append((prospect, result))
    return results


@task(name="personalize-emails")
async def personalize_emails(verified: list[tuple], niche: str, value_prop: str, language: str) -> list:
    """Run personalization pipeline for each verified prospect."""
    pipeline = PersonalizationPipeline(niche=niche, value_prop=value_prop, language=language)
    results = []
    for prospect, verif_result in verified:
        email = await pipeline.personalize(prospect)
        results.append({
            "prospect": prospect,
            "verif_result": verif_result,
            "email": email,
        })
    return results


@task(name="save-to-db")
async def save_prospects_and_emails(
    personalized: list,
    campaign_id: uuid.UUID,
    db: AsyncSession,
    review_pct: float,
) -> list[uuid.UUID]:
    """Persist prospects + emails to DB. Mark review emails as IN_REVIEW."""
    selector = ReviewSelector(review_pct=review_pct)

    # Build review eligibility data
    email_data_list = [
        {
            "id": str(uuid.uuid4()),
            "email_verification_score": item["verif_result"].score,
            "signal_type": item["email"].signal_type,
            "is_first_campaign": False,
        }
        for item in personalized
    ]
    review_ids = {e["id"] for e in selector.select_for_review(email_data_list)}

    saved_email_ids = []
    for i, item in enumerate(personalized):
        prospect_data = item["prospect"]
        verif = item["verif_result"]
        gen_email = item["email"]

        db_prospect = Prospect(
            campaign_id=campaign_id,
            first_name=prospect_data.first_name,
            last_name=prospect_data.last_name,
            role=prospect_data.role,
            email=prospect_data.email,
            linkedin_url=prospect_data.linkedin_url,
            company_name=prospect_data.company_name,
            company_size=prospect_data.company_size,
            industry=prospect_data.industry,
            geography=prospect_data.geography,
            enriched_data=prospect_data.enriched_data,
            icp_score=prospect_data.enriched_data.get("icp_score"),
            email_verification_score=verif.score,
            confirmed_sources=[s.value for s in prospect_data.confirmed_sources],
        )
        db.add(db_prospect)
        await db.flush()

        status = EmailStatus.IN_REVIEW if email_data_list[i]["id"] in review_ids else EmailStatus.APPROVED
        db_email = Email(
            prospect_id=db_prospect.id,
            subject=gen_email.subject,
            body=gen_email.body,
            icebreaker=gen_email.icebreaker,
            signal_type=gen_email.signal_type,
            signal_text=gen_email.signal_text,
            quality_score=gen_email.quality_score,
            status=status,
        )
        db.add(db_email)
        saved_email_ids.append(db_email.id)

    await db.commit()
    return saved_email_ids


@flow(name="campaign-pipeline", log_prints=True)
async def run_campaign_pipeline(
    campaign_id: str,
    icp_config: dict,
    batch_size: int,
    niche: str,
    value_prop: str,
    language: str,
    review_pct: float,
    db: AsyncSession,
):
    logger = get_run_logger()

    # Stage 1: Scrape
    prospects = await run_scraping_flow(campaign_id, icp_config, batch_size)
    logger.info(f"Scraped {len(prospects)} ICP-filtered prospects")

    # Stage 2: Verify emails
    verified = await verify_emails(prospects)
    logger.info(f"Email verification: {len(verified)}/{len(prospects)} passed")

    # Stage 3: Personalize
    personalized = await personalize_emails(verified, niche, value_prop, language)
    flagged = sum(1 for p in personalized if p["email"].flagged_for_manual)
    logger.info(f"Personalization: {len(personalized)} emails generated, {flagged} flagged for manual")

    # Stage 4: Save to DB with review queue assignment
    email_ids = await save_prospects_and_emails(
        personalized, uuid.UUID(campaign_id), db, review_pct
    )
    logger.info(f"Saved {len(email_ids)} emails to DB")

    return {
        "campaign_id": campaign_id,
        "total_prospects": len(prospects),
        "verified": len(verified),
        "emails_generated": len(personalized),
        "flagged_for_manual": flagged,
    }
