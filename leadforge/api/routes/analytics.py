import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from leadforge.database import get_db
from leadforge.models.campaign import Campaign
from leadforge.models.prospect import Prospect
from leadforge.models.email import Email, EmailStatus
from leadforge.models.client import Client
from leadforge.api.deps import get_current_client

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
async def get_summary(
    db: AsyncSession = Depends(get_db),
    current: Client = Depends(get_current_client),
):
    """Aggregate stats across all campaigns for this client."""
    # Active campaigns
    camp_result = await db.execute(
        select(func.count()).where(Campaign.client_id == current.id, Campaign.is_active.is_(True))
    )
    active_campaigns = camp_result.scalar() or 0

    # All campaign IDs for this client
    camp_ids_result = await db.execute(
        select(Campaign.id).where(Campaign.client_id == current.id)
    )
    camp_ids = [r[0] for r in camp_ids_result.fetchall()]

    emails_sent = 0
    pending_review = 0

    if camp_ids:
        sent_result = await db.execute(
            select(func.count(Email.id)).join(Prospect).join(Campaign).where(
                Campaign.client_id == current.id,
                Email.status == EmailStatus.APPROVED,
            )
        )
        emails_sent = sent_result.scalar() or 0

        pending_result = await db.execute(
            select(func.count(Email.id)).join(Prospect).join(Campaign).where(
                Campaign.client_id == current.id,
                Email.status == EmailStatus.IN_REVIEW,
            )
        )
        pending_review = pending_result.scalar() or 0

    return {
        "active_campaigns": active_campaigns,
        "emails_sent": emails_sent,
        "pending_review": pending_review,
        "avg_open_rate": None,   # populated by Instantly poller in future
        "avg_reply_rate": None,
    }


@router.get("/{campaign_id}")
async def get_campaign_analytics(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current: Client = Depends(get_current_client),
):
    """Stats for a single campaign."""
    # Verify ownership
    camp_result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id, Campaign.client_id == current.id)
    )
    campaign = camp_result.scalar_one_or_none()
    if not campaign:
        return {"error": "not found"}

    total_result = await db.execute(
        select(func.count(Email.id)).join(Prospect).where(Prospect.campaign_id == campaign_id)
    )
    total = total_result.scalar() or 0

    approved_result = await db.execute(
        select(func.count(Email.id)).join(Prospect).where(
            Prospect.campaign_id == campaign_id,
            Email.status == EmailStatus.APPROVED,
        )
    )
    approved = approved_result.scalar() or 0

    pending_result = await db.execute(
        select(func.count(Email.id)).join(Prospect).where(
            Prospect.campaign_id == campaign_id,
            Email.status == EmailStatus.IN_REVIEW,
        )
    )
    pending = pending_result.scalar() or 0

    avg_score_result = await db.execute(
        select(func.avg(Email.quality_score)).join(Prospect).where(
            Prospect.campaign_id == campaign_id
        )
    )
    avg_score = round(avg_score_result.scalar() or 0, 1)

    return {
        "campaign_id": str(campaign_id),
        "name": campaign.name,
        "pipeline_status": campaign.pipeline_status,
        "total_emails": total,
        "approved": approved,
        "pending_review": pending,
        "rejected": total - approved - pending,
        "avg_quality_score": avg_score,
        "open_rate": None,   # from Instantly poller
        "reply_rate": None,
    }
