import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from leadforge.database import get_db
from leadforge.models.campaign import Campaign
from leadforge.models.client import Client
from leadforge.schemas.campaign import CampaignCreate, CampaignRead
from leadforge.api.deps import get_current_client

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.post("/", response_model=CampaignRead, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    payload: CampaignCreate,
    db: AsyncSession = Depends(get_db),
    current: Client = Depends(get_current_client),
):
    campaign = Campaign(client_id=current.id, **payload.model_dump())
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return campaign


@router.get("/", response_model=list[CampaignRead])
async def list_campaigns(
    db: AsyncSession = Depends(get_db),
    current: Client = Depends(get_current_client),
):
    result = await db.execute(
        select(Campaign).where(Campaign.client_id == current.id, Campaign.is_active == True)
    )
    return result.scalars().all()
