import uuid
from pydantic import BaseModel, Field


class CampaignCreate(BaseModel):
    name: str
    niche: str | None = None
    value_prop: str | None = None
    language: str = "en"
    batch_size: int = 25
    review_pct: float = 15.0
    icp_config: dict = Field(default_factory=dict)
    scraping_config: dict = Field(default_factory=dict)
    personalization_config: dict = Field(default_factory=dict)
    verification_config: dict = Field(default_factory=dict)


class CampaignRead(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    name: str
    niche: str | None
    value_prop: str | None
    language: str
    batch_size: int
    review_pct: float
    is_active: bool
    pipeline_status: str

    model_config = {"from_attributes": True}
