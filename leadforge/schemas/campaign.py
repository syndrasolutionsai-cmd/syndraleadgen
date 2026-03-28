import uuid
from pydantic import BaseModel


class CampaignCreate(BaseModel):
    name: str
    niche: str | None = None
    language: str = "en"
    batch_size: int = 500
    icp_config: dict = {}
    scraping_config: dict = {}
    personalization_config: dict = {}
    verification_config: dict = {}


class CampaignRead(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    name: str
    niche: str | None
    language: str
    batch_size: int
    is_active: bool

    model_config = {"from_attributes": True}
