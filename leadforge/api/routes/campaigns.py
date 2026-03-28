import uuid
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from leadforge.database import get_db, AsyncSessionLocal
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
        select(Campaign).where(Campaign.client_id == current.id, Campaign.is_active.is_(True))
    )
    return result.scalars().all()


@router.get("/{campaign_id}", response_model=CampaignRead)
async def get_campaign(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current: Client = Depends(get_current_client),
):
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id, Campaign.client_id == current.id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


async def _run_pipeline(campaign_id: str, campaign_data: dict):
    from leadforge.workflows.pipeline_flow import run_campaign_pipeline
    async with AsyncSessionLocal() as db:
        await run_campaign_pipeline(
            campaign_id=campaign_id,
            icp_config=campaign_data["icp_config"],
            batch_size=campaign_data["batch_size"],
            niche=campaign_data["niche"] or "",
            value_prop=campaign_data["value_prop"] or "",
            language=campaign_data["language"],
            review_pct=campaign_data["review_pct"],
            db=db,
        )


@router.post("/{campaign_id}/launch", status_code=status.HTTP_202_ACCEPTED)
async def launch_campaign(
    campaign_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current: Client = Depends(get_current_client),
):
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id, Campaign.client_id == current.id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    campaign_data = {
        "icp_config": campaign.icp_config,
        "batch_size": campaign.batch_size,
        "niche": campaign.niche,
        "value_prop": campaign.value_prop,
        "language": campaign.language,
        "review_pct": campaign.review_pct,
    }
    background_tasks.add_task(_run_pipeline, str(campaign_id), campaign_data)
    return {"status": "launched", "campaign_id": str(campaign_id)}
