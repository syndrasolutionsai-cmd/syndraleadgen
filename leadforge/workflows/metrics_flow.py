# leadforge/workflows/metrics_flow.py
from prefect import flow, task, get_run_logger
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from leadforge.instantly.poller import MetricsPoller
from leadforge.models.campaign import Campaign
from leadforge.database import AsyncSessionLocal
from leadforge.crypto import decrypt


@flow(name="metrics-poll", log_prints=True)
async def run_metrics_poll():
    """Poll Instantly for metrics for all active campaigns with an Instantly campaign ID."""
    logger = get_run_logger()

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Campaign)
            .options(selectinload(Campaign.client))
            .where(Campaign.is_active == True)
        )
        campaigns = result.scalars().all()

        for campaign in campaigns:
            instantly_campaign_id = campaign.personalization_config.get("instantly_campaign_id")
            if not instantly_campaign_id:
                continue

            if not campaign.client or not campaign.client.instantly_api_key_enc:
                continue

            api_key = decrypt(campaign.client.instantly_api_key_enc)
            poller = MetricsPoller(instantly_api_key=api_key, db=db)

            try:
                metrics = await poller.poll_campaign(instantly_campaign_id, str(campaign.id))
                campaign.personalization_config = {
                    **campaign.personalization_config,
                    "metrics": metrics,
                }
                await db.commit()
                logger.info(
                    f"Campaign {campaign.name}: open_rate={metrics['open_rate']:.1%}, "
                    f"reply_rate={metrics['reply_rate']:.1%}"
                )
            except Exception as e:
                logger.error(f"Failed to poll campaign {campaign.id}: {e}")
