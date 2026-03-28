# leadforge/api/routes/review.py
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from leadforge.database import get_db
from leadforge.models.email import Email, EmailStatus
from leadforge.models.prospect import Prospect
from leadforge.models.campaign import Campaign
from leadforge.models.client import Client
from leadforge.api.deps import get_current_client

router = APIRouter(prefix="/review", tags=["review"])


@router.get("/{campaign_id}")
async def get_review_queue(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current: Client = Depends(get_current_client),
):
    """Get emails pending human review for a campaign."""
    # Verify campaign belongs to this client
    camp_result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id, Campaign.client_id == current.id)
    )
    if not camp_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Campaign not found")

    result = await db.execute(
        select(Email, Prospect)
        .join(Prospect, Email.prospect_id == Prospect.id)
        .where(
            Prospect.campaign_id == campaign_id,
            Email.status == EmailStatus.IN_REVIEW,
        )
    )
    rows = result.all()
    return [
        {
            "email_id": str(email.id),
            "prospect_name": f"{prospect.first_name} {prospect.last_name}",
            "company": prospect.company_name,
            "role": prospect.role,
            "email_address": prospect.email,
            "subject": email.subject,
            "body": email.body,
            "icebreaker": email.icebreaker,
            "signal_type": email.signal_type,
            "signal_text": email.signal_text,
            "quality_score": email.quality_score,
            "email_verification_score": prospect.email_verification_score,
        }
        for email, prospect in rows
    ]


@router.post("/approve/{email_id}", status_code=200)
async def approve_email(
    email_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current: Client = Depends(get_current_client),
):
    """Mark an email as approved."""
    email = await _get_owned_email(email_id, db, current)
    email.status = EmailStatus.APPROVED
    await db.commit()
    return {"status": "approved"}


@router.post("/reject/{email_id}", status_code=200)
async def reject_email(
    email_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current: Client = Depends(get_current_client),
):
    """Mark an email as rejected."""
    email = await _get_owned_email(email_id, db, current)
    email.status = EmailStatus.REJECTED
    await db.commit()
    return {"status": "rejected"}


@router.put("/edit/{email_id}", status_code=200)
async def edit_email(
    email_id: uuid.UUID,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current: Client = Depends(get_current_client),
):
    """Edit and approve an email."""
    email = await _get_owned_email(email_id, db, current)
    if "subject" in payload:
        email.subject = payload["subject"]
    if "body" in payload:
        email.body = payload["body"]
    email.status = EmailStatus.APPROVED
    await db.commit()
    return {"status": "edited_and_approved"}


async def _get_owned_email(email_id: uuid.UUID, db: AsyncSession, current: Client) -> Email:
    """Fetch email and verify it belongs to the current client."""
    result = await db.execute(
        select(Email)
        .join(Prospect, Email.prospect_id == Prospect.id)
        .join(Campaign, Prospect.campaign_id == Campaign.id)
        .where(Email.id == email_id, Campaign.client_id == current.id)
    )
    email = result.scalar_one_or_none()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email
